"""Sequential build execution: check.py -> package.py, one build at a time.

All builds (manual, weekly-scheduled, or triggered via MCP) are pushed onto a
single FIFO queue consumed by one dedicated worker thread, guaranteeing that
package_universal_cap is never executed concurrently.
"""
import datetime
import logging
import os
import queue
import threading
import time
from dataclasses import dataclass

from sqlalchemy import select

from app.core.database import SyncSessionLocal
from app.core.models import BuildFile, BuildHistory, Project
from app.core.package import package_universal_cap
from app.core.check import check_ids
from app.core.storage import enforce_retention
from app.core.config import get_settings
from app.service.mail_service import send_email

logger = logging.getLogger(__name__)
settings = get_settings()


@dataclass
class BuildJob:
    build_history_id: int
    project_id: int
    project_name: str
    token: str


_job_queue: "queue.Queue[BuildJob]" = queue.Queue()
_worker_started = threading.Event()


def submit_build(project_id: int, project_name: str, token: str, trigger: str = "manual") -> int:
    """Creates an `in_progress` BuildHistory row and enqueues the job. Returns its id."""
    with SyncSessionLocal() as db:
        history = BuildHistory(project_id=project_id, build_status="in_progress", trigger=trigger)
        db.add(history)
        db.commit()
        db.refresh(history)
        build_history_id = history.id

    _job_queue.put(BuildJob(build_history_id, project_id, project_name, token))
    return build_history_id


def wait_for_completion(build_history_id: int, timeout: float = 300.0) -> BuildHistory | None:
    """Polls the database until the given build finishes, or timeout elapses."""
    deadline = time.monotonic() + timeout
    while time.monotonic() < deadline:
        with SyncSessionLocal() as db:
            history = db.get(BuildHistory, build_history_id)
            if history is not None and history.build_status != "in_progress":
                db.expunge(history)
                return history
        time.sleep(0.5)
    return None


def _last_success_ids(db, project_id: int, exclude_history_id: int) -> list[str]:
    last = db.scalars(
        select(BuildHistory)
        .where(
            BuildHistory.project_id == project_id,
            BuildHistory.build_status == "success",
            BuildHistory.id != exclude_history_id,
        )
        .order_by(BuildHistory.started_at.desc())
    ).first()
    return last.ids_used if last else []


def _notify_failure(project_name: str, error: str) -> None:
    if not settings.notify_emails:
        return
    for recipient in settings.notify_emails:
        try:
            send_email(recipient, f"[Mikura] Build failed: {project_name}", error)
        except Exception:
            logger.exception("Failed to send build failure notification to %s", recipient)


def _process_job(job: BuildJob) -> None:
    with SyncSessionLocal() as db:
        history = db.get(BuildHistory, job.build_history_id)
        if history is None:
            logger.error("BuildHistory %s not found", job.build_history_id)
            return

        try:
            previous_ids = _last_success_ids(db, job.project_id, job.build_history_id)
            if previous_ids and not check_ids(job.project_name, previous_ids):
                history.build_status = "failed"
                history.error_message = "check.py verification failed: not ok to build"
                history.completed_at = datetime.datetime.now(datetime.timezone.utc)
                db.commit()
                _notify_failure(job.project_name, history.error_message)
                return

            result = package_universal_cap(job.project_name, job.token)
            output_path = result["packaged_file_path"]
            ids_used = result["ids_used_for_packaging"]

            history.build_status = "success"
            history.completed_at = datetime.datetime.now(datetime.timezone.utc)
            history.output_file_path = output_path
            history.ids_used = ids_used
            db.commit()

            build_file = BuildFile(
                project_id=job.project_id,
                build_history_id=history.id,
                file_name=os.path.basename(output_path),
                file_path=output_path,
            )
            db.add(build_file)
            db.commit()

            enforce_retention(db, job.project_id, job.project_name)
        except Exception as exc:  # noqa: BLE001 - build failures must not crash the worker
            logger.exception("Build failed for project %s", job.project_name)
            history.build_status = "failed"
            history.error_message = str(exc)
            history.completed_at = datetime.datetime.now(datetime.timezone.utc)
            db.commit()
            _notify_failure(job.project_name, str(exc))


def _worker_loop() -> None:
    while True:
        job = _job_queue.get()
        try:
            _process_job(job)
        finally:
            _job_queue.task_done()


def start_worker() -> None:
    """Starts the single background build-worker thread (idempotent)."""
    if _worker_started.is_set():
        return
    _worker_started.set()
    thread = threading.Thread(target=_worker_loop, name="mikura-build-worker", daemon=True)
    thread.start()


def build_from_project_name(project_name: str, token: str, trigger: str = "manual") -> int:
    """Resolves a project by name and submits a build; used by MCP tools."""
    with SyncSessionLocal() as db:
        project = db.scalars(select(Project).where(Project.name == project_name)).first()
        if project is None:
            raise ValueError(f"Unknown project '{project_name}'")
        project_id = project.id
    return submit_build(project_id, project_name, token, trigger)

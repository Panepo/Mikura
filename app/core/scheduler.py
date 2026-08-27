"""Weekly build scheduler backed by APScheduler.

Each active `BuildSchedule` row gets a corresponding APScheduler cron job. A
static bearer token (SHIGURE_TOKEN) is used for these unattended runs (no
interactive user is available for scheduled builds).
"""
import logging

from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger
from sqlalchemy import select

from app.core.build_runner import submit_build
from app.core.config import get_settings
from app.core.database import SyncSessionLocal
from app.core.models import BuildSchedule, Project

logger = logging.getLogger(__name__)
settings = get_settings()

scheduler = BackgroundScheduler()


def _job_id(project_id: int) -> str:
    return f"weekly-build-project-{project_id}"


def _run_scheduled_build(project_id: int, project_name: str) -> None:
    if not settings.shigure_token:
        logger.error(
            "Cannot run scheduled build for '%s': SHIGURE_TOKEN not configured",
            project_name,
        )
        return

    submit_build(project_id, project_name, settings.shigure_token, trigger="weekly")


def register_schedule(project_id: int, project_name: str, day_of_week: str, hour: int, minute: int) -> None:
    scheduler.add_job(
        _run_scheduled_build,
        trigger=CronTrigger(day_of_week=day_of_week, hour=hour, minute=minute),
        args=[project_id, project_name],
        id=_job_id(project_id),
        replace_existing=True,
    )


def unregister_schedule(project_id: int) -> None:
    job_id = _job_id(project_id)
    if scheduler.get_job(job_id):
        scheduler.remove_job(job_id)


def load_active_schedules() -> None:
    with SyncSessionLocal() as db:
        schedules = db.scalars(select(BuildSchedule).where(BuildSchedule.is_active.is_(True)))
        for schedule in schedules:
            project = db.get(Project, schedule.project_id)
            if project is None:
                continue
            register_schedule(project.id, project.name, schedule.day_of_week, schedule.hour, schedule.minute)


def start_scheduler() -> None:
    if not scheduler.running:
        load_active_schedules()
        scheduler.start()


def shutdown_scheduler() -> None:
    if scheduler.running:
        scheduler.shutdown(wait=False)

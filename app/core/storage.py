"""File retention: keep only the N latest build files per project."""
import logging
import os

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.config import get_settings
from app.core.models import BuildFile
from app.service.mail_service import send_email

logger = logging.getLogger(__name__)
settings = get_settings()


def enforce_retention(db: Session, project_id: int, project_name: str) -> list[BuildFile]:
    """Delete build files older than the `build_retention_count` newest ones.

    Returns the list of removed BuildFile rows (already deleted from the session).
    """
    files = list(
        db.scalars(
            select(BuildFile)
            .where(BuildFile.project_id == project_id)
            .order_by(BuildFile.created_at.desc())
        )
    )

    stale = files[settings.build_retention_count :]
    removed: list[BuildFile] = []
    for build_file in stale:
        try:
            if os.path.exists(build_file.file_path):
                os.remove(build_file.file_path)
        except OSError:
            logger.exception("Failed to remove build file %s", build_file.file_path)
            continue
        db.delete(build_file)
        removed.append(build_file)

    if removed:
        db.commit()
        _notify_cleanup(project_name, removed)

    return removed


def _notify_cleanup(project_name: str, removed: list[BuildFile]) -> None:
    if not settings.notify_emails:
        return
    names = ", ".join(f.file_name for f in removed)
    body = f"Retention cleanup for project '{project_name}' removed {len(removed)} old file(s): {names}"
    for recipient in settings.notify_emails:
        try:
            send_email(recipient, f"[Mikura] Retention cleanup: {project_name}", body)
        except Exception:
            logger.exception("Failed to send retention cleanup notification to %s", recipient)

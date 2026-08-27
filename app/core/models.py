"""SQLAlchemy ORM models for project scheduling, build history and file retention."""
import datetime
import json

from sqlalchemy import DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base


def _utcnow() -> datetime.datetime:
    return datetime.datetime.now(datetime.timezone.utc)


class Project(Base):
    __tablename__ = "projects"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(255), unique=True, index=True)
    description: Mapped[str] = mapped_column(Text, default="")
    status: Mapped[str] = mapped_column(String(32), default="active")
    created_at: Mapped[datetime.datetime] = mapped_column(DateTime(timezone=True), default=_utcnow)
    updated_at: Mapped[datetime.datetime] = mapped_column(
        DateTime(timezone=True), default=_utcnow, onupdate=_utcnow
    )

    schedule: Mapped["BuildSchedule | None"] = relationship(
        back_populates="project", uselist=False, cascade="all, delete-orphan"
    )
    histories: Mapped[list["BuildHistory"]] = relationship(
        back_populates="project", cascade="all, delete-orphan", order_by="desc(BuildHistory.started_at)"
    )
    files: Mapped[list["BuildFile"]] = relationship(
        back_populates="project", cascade="all, delete-orphan", order_by="desc(BuildFile.created_at)"
    )


class BuildSchedule(Base):
    __tablename__ = "build_schedules"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    project_id: Mapped[int] = mapped_column(ForeignKey("projects.id"), unique=True)
    schedule_type: Mapped[str] = mapped_column(String(32), default="weekly")
    day_of_week: Mapped[str] = mapped_column(String(16), default="mon")
    hour: Mapped[int] = mapped_column(Integer, default=2)
    minute: Mapped[int] = mapped_column(Integer, default=0)
    next_run_time: Mapped[datetime.datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    is_active: Mapped[bool] = mapped_column(default=True)
    created_at: Mapped[datetime.datetime] = mapped_column(DateTime(timezone=True), default=_utcnow)
    updated_at: Mapped[datetime.datetime] = mapped_column(
        DateTime(timezone=True), default=_utcnow, onupdate=_utcnow
    )

    project: Mapped[Project] = relationship(back_populates="schedule")


class BuildHistory(Base):
    __tablename__ = "build_histories"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    project_id: Mapped[int] = mapped_column(ForeignKey("projects.id"), index=True)
    build_status: Mapped[str] = mapped_column(String(32), default="in_progress")  # success/failed/in_progress
    trigger: Mapped[str] = mapped_column(String(16), default="manual")  # manual/weekly/mcp
    started_at: Mapped[datetime.datetime] = mapped_column(DateTime(timezone=True), default=_utcnow)
    completed_at: Mapped[datetime.datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    output_file_path: Mapped[str | None] = mapped_column(String(1024), nullable=True)
    ids_used_json: Mapped[str] = mapped_column(Text, default="[]")
    error_message: Mapped[str | None] = mapped_column(Text, nullable=True)

    project: Mapped[Project] = relationship(back_populates="histories")

    @property
    def ids_used(self) -> list[str]:
        return json.loads(self.ids_used_json or "[]")

    @ids_used.setter
    def ids_used(self, value: list[str]) -> None:
        self.ids_used_json = json.dumps(value)


class BuildFile(Base):
    __tablename__ = "build_files"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    project_id: Mapped[int] = mapped_column(ForeignKey("projects.id"), index=True)
    build_history_id: Mapped[int] = mapped_column(ForeignKey("build_histories.id"))
    file_name: Mapped[str] = mapped_column(String(512))
    file_path: Mapped[str] = mapped_column(String(1024))
    created_at: Mapped[datetime.datetime] = mapped_column(DateTime(timezone=True), default=_utcnow)

    project: Mapped[Project] = relationship(back_populates="files")

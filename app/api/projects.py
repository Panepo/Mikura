"""Project management & weekly build scheduling endpoints (managers only)."""
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.schemas import (
    BuildFileOut,
    BuildHistoryOut,
    BuildTriggerResponse,
    ProjectCreate,
    ProjectOut,
    ScheduleRequest,
    ShigureProjectResult,
)
from app.core import scheduler as scheduler_module
from app.core.build_runner import submit_build
from app.core.config import get_settings
from app.core.database import get_db
from app.core.models import BuildFile, BuildHistory, BuildSchedule, Project
from app.core.security import CurrentUser, require_manager
from app.service import shigure_client
from app.service.shigure_client import ShigureApiError

router = APIRouter(prefix="/projects", tags=["projects"])
settings = get_settings()


@router.get("/shigure/search", response_model=list[ShigureProjectResult])
async def search_shigure_projects(
    q: str = Query(..., min_length=1), user: CurrentUser = Depends(require_manager)
):
    if not settings.shigure_token:
        raise HTTPException(status_code=500, detail="SHIGURE_TOKEN is not configured")
    try:
        results = await shigure_client.query_projects(q, settings.shigure_token)
    except ShigureApiError as exc:
        raise HTTPException(status_code=exc.status_code, detail=exc.detail) from exc
    return results


@router.get("/", response_model=list[ProjectOut])
async def list_projects(
    db: AsyncSession = Depends(get_db), user: CurrentUser = Depends(require_manager)
):
    result = await db.scalars(select(Project).order_by(Project.name))
    return list(result)


@router.post("/", response_model=ProjectOut, status_code=201)
async def create_project(
    payload: ProjectCreate,
    db: AsyncSession = Depends(get_db),
    user: CurrentUser = Depends(require_manager),
):
    existing = await db.scalar(select(Project).where(Project.name == payload.name))
    if existing:
        raise HTTPException(status_code=409, detail="Project already exists")
    project = Project(name=payload.name, description=payload.description)
    db.add(project)
    await db.commit()
    await db.refresh(project)
    return project


async def _get_project_or_404(db: AsyncSession, project_id: int) -> Project:
    project = await db.get(Project, project_id)
    if project is None:
        raise HTTPException(status_code=404, detail="Project not found")
    return project


@router.post("/{project_id}/schedule")
async def set_schedule(
    project_id: int,
    payload: ScheduleRequest,
    db: AsyncSession = Depends(get_db),
    user: CurrentUser = Depends(require_manager),
):
    project = await _get_project_or_404(db, project_id)

    existing = await db.scalar(select(BuildSchedule).where(BuildSchedule.project_id == project_id))
    if existing:
        existing.is_active = payload.is_active
        existing.day_of_week = payload.day_of_week
        existing.hour = payload.hour
        existing.minute = payload.minute
    else:
        existing = BuildSchedule(
            project_id=project_id,
            is_active=payload.is_active,
            day_of_week=payload.day_of_week,
            hour=payload.hour,
            minute=payload.minute,
        )
        db.add(existing)
    await db.commit()

    if payload.is_active:
        scheduler_module.register_schedule(
            project_id, project.name, payload.day_of_week, payload.hour, payload.minute
        )
    else:
        scheduler_module.unregister_schedule(project_id)

    return {"message": "Schedule updated"}


@router.post("/{project_id}/build", response_model=BuildTriggerResponse)
async def trigger_build(
    project_id: int,
    db: AsyncSession = Depends(get_db),
    user: CurrentUser = Depends(require_manager),
):
    project = await _get_project_or_404(db, project_id)
    build_history_id = submit_build(project.id, project.name, user.token, trigger="manual")
    return BuildTriggerResponse(build_history_id=build_history_id, status="queued")


@router.get("/{project_id}/status", response_model=BuildHistoryOut | None)
async def get_status(
    project_id: int,
    db: AsyncSession = Depends(get_db),
    user: CurrentUser = Depends(require_manager),
):
    await _get_project_or_404(db, project_id)
    latest = await db.scalar(
        select(BuildHistory)
        .where(BuildHistory.project_id == project_id)
        .order_by(BuildHistory.started_at.desc())
    )
    return latest


@router.get("/{project_id}/files/", response_model=list[BuildFileOut])
async def list_files(
    project_id: int,
    db: AsyncSession = Depends(get_db),
    user: CurrentUser = Depends(require_manager),
):
    await _get_project_or_404(db, project_id)
    result = await db.scalars(
        select(BuildFile).where(BuildFile.project_id == project_id).order_by(BuildFile.created_at.desc())
    )
    return list(result)

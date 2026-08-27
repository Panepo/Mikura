"""Server-rendered HTML pages: login, dashboard, and file download."""
import os

from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.responses import FileResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.models import BuildFile
from app.core.security import CurrentUser, require_manager_query

router = APIRouter(tags=["pages"])
templates = Jinja2Templates(directory="app/templates")


@router.get("/login")
async def login_page(request: Request):
    return templates.TemplateResponse(request, "login.html")


@router.get("/dashboard")
async def dashboard_page(request: Request):
    return templates.TemplateResponse(request, "dashboard.html")


@router.get("/download/{project_id}/{file_id}")
async def download_file(
    project_id: int,
    file_id: int,
    db: AsyncSession = Depends(get_db),
    user: CurrentUser = Depends(require_manager_query),
):
    build_file = await db.scalar(
        select(BuildFile).where(BuildFile.id == file_id, BuildFile.project_id == project_id)
    )
    if build_file is None or not os.path.exists(build_file.file_path):
        raise HTTPException(status_code=404, detail="File not found")

    return FileResponse(build_file.file_path, filename=build_file.file_name)

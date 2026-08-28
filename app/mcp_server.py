"""MCP server exposing package/list/download tools for the universal cap system.

Mounted onto the FastAPI app at `/mcp` (streamable HTTP transport).

Unlike the web dashboard (which logs in once via the browser and stores a JWT
in localStorage), each MCP tool call is stateless, so every tool other than
`login` requires a `token` argument obtained from the `login` tool first.
"""
from jose import JWTError
from sqlalchemy import select

from mcp.server.fastmcp import FastMCP

from app.core.build_runner import build_from_project_name, wait_for_completion
from app.core.config import get_settings
from app.core.database import SyncSessionLocal
from app.core.models import BuildFile, Project
from app.core.security import CurrentUser, resolve_user_from_token
from app.service import shigure_client
from app.service.shigure_client import ShigureApiError

mcp = FastMCP("mikura", streamable_http_path="/")
settings = get_settings()


def _authorize(token: str) -> CurrentUser:
    """Validates a token obtained from `login` and requires manager access,
    mirroring the web dashboard's `require_manager` gate."""
    if not token:
        raise ValueError("Missing token. Call the `login` tool first to obtain one.")
    try:
        user = resolve_user_from_token(token)
    except JWTError as exc:
        raise ValueError("Invalid or expired token. Call the `login` tool again.") from exc
    if not settings.is_manager(user.id):
        raise ValueError("Manager access required for this tool.")
    return user


@mcp.tool()
async def login(username: str, password: str) -> dict:
    """Log in to Shigure and obtain a token. Call this before any other tool;
    pass the returned token to `package`, `list`, and `download`.

    Args:
        username: Shigure account username.
        password: Shigure account password.
    """
    try:
        return await shigure_client.login(username, password)
    except ShigureApiError as exc:
        raise ValueError(f"Login failed: {exc.detail}") from exc


@mcp.tool()
def package(project_name: str, token: str) -> dict:
    """Trigger the universal cap packaging process for a project and wait for the result.

    Args:
        project_name: Name of the project to package.
        token: Token obtained from the `login` tool.
    """
    _authorize(token)
    build_history_id = build_from_project_name(project_name, token, trigger="mcp")
    history = wait_for_completion(build_history_id)
    if history is None:
        return {"build_history_id": build_history_id, "status": "timeout"}
    return {
        "build_history_id": history.id,
        "status": history.build_status,
        "output_file_path": history.output_file_path,
        "ids_used": history.ids_used,
        "error_message": history.error_message,
    }


@mcp.tool(name="list")
def list_files(project_name: str, token: str) -> list[dict]:
    """List available packaged universal cap files for a project.

    Args:
        project_name: Name of the project.
        token: Token obtained from the `login` tool.
    """
    _authorize(token)
    with SyncSessionLocal() as db:
        project = db.scalars(select(Project).where(Project.name == project_name)).first()
        if project is None:
            raise ValueError(f"Unknown project '{project_name}'")
        files = db.scalars(
            select(BuildFile).where(BuildFile.project_id == project.id).order_by(BuildFile.created_at.desc())
        )
        return [
            {
                "file_id": f.id,
                "file_name": f.file_name,
                "file_path": f.file_path,
                "created_at": f.created_at.isoformat(),
            }
            for f in files
        ]


@mcp.tool()
def list_projects(token: str) -> list[dict]:
    """List all currently registered projects.

    Args:
        token: Token obtained from the `login` tool.
    """
    _authorize(token)
    with SyncSessionLocal() as db:
        projects = db.scalars(select(Project).order_by(Project.name)).all()
        return [
            {
                "id": p.id,
                "name": p.name,
                "description": p.description,
                "status": p.status,
                "created_at": p.created_at.isoformat(),
                "updated_at": p.updated_at.isoformat(),
            }
            for p in projects
        ]


@mcp.tool()
def download(project_id: int, file_id: int, token: str) -> dict:
    """Return the location of a specific packaged universal cap file.

    The actual bytes should be retrieved via the HTTP endpoint
    `GET /download/{project_id}/{file_id}?token=...`.

    Args:
        project_id: Project id the file belongs to.
        file_id: File id to look up.
        token: Token obtained from the `login` tool.
    """
    _authorize(token)
    with SyncSessionLocal() as db:
        build_file = db.scalars(
            select(BuildFile).where(BuildFile.id == file_id, BuildFile.project_id == project_id)
        ).first()
        if build_file is None:
            raise ValueError("File not found")
        return {
            "file_name": build_file.file_name,
            "file_path": build_file.file_path,
            "download_url": f"/download/{project_id}/{file_id}",
        }

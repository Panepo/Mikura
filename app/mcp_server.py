"""MCP server exposing package/list/download tools for the universal cap system.

Mounted onto the FastAPI app at `/mcp` (streamable HTTP transport).
"""
from sqlalchemy import select

from mcp.server.fastmcp import FastMCP

from app.core.build_runner import build_from_project_name, wait_for_completion
from app.core.database import SyncSessionLocal
from app.core.models import BuildFile, Project

mcp = FastMCP("mikura", streamable_http_path="/")


@mcp.tool()
def package(project_name: str, token: str) -> dict:
    """Trigger the universal cap packaging process for a project and wait for the result.

    Args:
        project_name: Name of the project to package.
        token: Shigure auth token (obtained from user login) used to run the build.
    """
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
def list_files(project_name: str) -> list[dict]:
    """List available packaged universal cap files for a project."""
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
def download(project_id: int, file_id: int) -> dict:
    """Return the location of a specific packaged universal cap file.

    The actual bytes should be retrieved via the HTTP endpoint
    `GET /download/{project_id}/{file_id}?token=...`.
    """
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

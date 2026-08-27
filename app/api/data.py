"""Data retrieval / upload / download endpoints proxied to the Shigure Data Center."""
from fastapi import APIRouter, Depends, HTTPException, Request, UploadFile
from fastapi.responses import Response

from app.core.security import CurrentUser, get_current_user
from app.service import shigure_client
from app.service.shigure_client import ShigureApiError

router = APIRouter(prefix="/data", tags=["data"])


@router.get("/{table}/")
async def find_all(table: str, request: Request, user: CurrentUser = Depends(get_current_user)):
    try:
        return await shigure_client.find_all(table, user.token, params=dict(request.query_params))
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except ShigureApiError as exc:
        raise HTTPException(status_code=exc.status_code, detail=exc.detail) from exc


@router.get("/{table}/{item_id}")
async def find_one(
    table: str, item_id: str, request: Request, user: CurrentUser = Depends(get_current_user)
):
    try:
        return await shigure_client.find_one(table, item_id, user.token, params=dict(request.query_params))
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except ShigureApiError as exc:
        raise HTTPException(status_code=exc.status_code, detail=exc.detail) from exc


@router.post("/upload/{item_id}")
async def upload_single(
    item_id: str,
    file: UploadFile,
    type: str,
    user: CurrentUser = Depends(get_current_user),
):
    content = await file.read()
    try:
        return await shigure_client.upload_single(item_id, user.token, content, file.filename, type)
    except ShigureApiError as exc:
        raise HTTPException(status_code=exc.status_code, detail=exc.detail) from exc


@router.post("/uploads/{item_id}")
async def upload_multiple(
    item_id: str,
    files: list[UploadFile],
    user: CurrentUser = Depends(get_current_user),
):
    uploads = []
    for f in files:
        content = await f.read()
        uploads.append({"filename": f.filename, "content": content, "size": len(content)})
    try:
        return await shigure_client.upload_multiple(item_id, user.token, uploads)
    except ShigureApiError as exc:
        raise HTTPException(status_code=exc.status_code, detail=exc.detail) from exc


@router.post("/download/{table}/{item_id}")
async def download(
    table: str,
    item_id: str,
    type: str | None = None,
    user: CurrentUser = Depends(get_current_user),
):
    try:
        upstream = await shigure_client.download(table, item_id, user.token, type)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except ShigureApiError as exc:
        raise HTTPException(status_code=exc.status_code, detail=exc.detail) from exc

    return Response(
        content=upstream.content,
        media_type=upstream.headers.get("content-type", "application/octet-stream"),
    )

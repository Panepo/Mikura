"""Auth endpoints: thin proxy to the Shigure Data Center auth API."""
from fastapi import APIRouter, Depends, HTTPException, status

from app.api.schemas import LoginRequest
from app.core.security import CurrentUser, get_current_user
from app.service import shigure_client
from app.service.shigure_client import ShigureApiError

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("")
async def login(payload: LoginRequest):
    try:
        return await shigure_client.login(payload.username, payload.password)
    except ShigureApiError as exc:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=exc.detail) from exc


@router.get("")
async def get_me(user: CurrentUser = Depends(get_current_user)):
    try:
        return await shigure_client.get_current_user(user.token)
    except ShigureApiError as exc:
        raise HTTPException(status_code=exc.status_code, detail=exc.detail) from exc

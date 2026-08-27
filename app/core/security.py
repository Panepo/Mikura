"""JWT handling and auth dependencies.

Tokens are issued by the external Shigure auth server (see Shigure Api-auth.md)
and passed through by this service. We decode the claims locally (without
signature verification, since the signing key belongs to Shigure) purely to
authorize access to Mikura's own endpoints; any call proxied to Shigure is
re-validated by Shigure itself using the raw bearer token.
"""
from dataclasses import dataclass

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from jose import JWTError, jwt

from app.core.config import get_settings

settings = get_settings()

_bearer_scheme = HTTPBearer(auto_error=False)


@dataclass
class CurrentUser:
    id: str
    name: str
    role: str
    level: str | None
    token: str


def _extract_claims(token: str) -> dict:
    try:
        return jwt.get_unverified_claims(token)
    except JWTError as exc:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid or malformed token"
        ) from exc


async def get_current_user(
    credentials: HTTPAuthorizationCredentials | None = Depends(_bearer_scheme),
) -> CurrentUser:
    if credentials is None or not credentials.credentials:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Missing bearer token")

    token = credentials.credentials
    claims = _extract_claims(token)
    return CurrentUser(
        id=str(claims.get("sub", claims.get("id", ""))),
        name=str(claims.get("name", "")),
        role=str(claims.get("role", "")),
        level=claims.get("level"),
        token=token,
    )


async def get_token_from_query_or_header(
    token: str | None = None,
    credentials: HTTPAuthorizationCredentials | None = Depends(_bearer_scheme),
) -> CurrentUser:
    """Allows the token via `Authorization` header OR a `token` query parameter.

    Needed for browser-initiated file downloads where custom headers can't be set.
    """
    raw_token = credentials.credentials if credentials else token
    if not raw_token:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Missing bearer token")

    claims = _extract_claims(raw_token)
    return CurrentUser(
        id=str(claims.get("sub", claims.get("id", ""))),
        name=str(claims.get("name", "")),
        role=str(claims.get("role", "")),
        level=claims.get("level"),
        token=raw_token,
    )


def require_manager(user: CurrentUser = Depends(get_current_user)) -> CurrentUser:
    if not settings.is_manager(user.id):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Manager access required")
    return user


def require_manager_query(user: CurrentUser = Depends(get_token_from_query_or_header)) -> CurrentUser:
    if not settings.is_manager(user.id):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Manager access required")
    return user

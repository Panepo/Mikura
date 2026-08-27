"""HTTP client for the external Shigure Data Center API.

Implements the endpoints described in `.github/reference/Shigure Api-auth.md`
and `.github/reference/Shigure Api-data.md`. Mikura acts as a thin proxy: it
forwards the caller's credentials/token and relays the response.
"""
from typing import Any

import httpx

from app.core.config import get_settings

settings = get_settings()

_SUPPORTED_TABLES = {
    "driver",
    "driverprj",
    "bios",
    "biosprj",
    "ec",
    "ecprj",
    "app",
    "appprj",
    "file",
    "appfile",
}


class ShigureApiError(Exception):
    def __init__(self, status_code: int, detail: Any):
        self.status_code = status_code
        self.detail = detail
        super().__init__(f"Shigure API error {status_code}: {detail}")


def _auth_headers(token: str) -> dict:
    return {"Authorization": f"Bearer {token}"}


async def _request(method: str, path: str, **kwargs) -> httpx.Response:
    url = f"{settings.shigure_api_base_url.rstrip('/')}{path}"
    async with httpx.AsyncClient(timeout=30.0) as client:
        response = await client.request(method, url, **kwargs)
    if response.status_code >= 400:
        try:
            detail = response.json()
        except ValueError:
            detail = response.text
        raise ShigureApiError(response.status_code, detail)
    return response


async def login(username: str, password: str) -> dict:
    response = await _request("POST", "/auth", json={"email": username, "password": password, "server": "shigure"})
    return response.json()


async def get_current_user(token: str) -> dict:
    response = await _request("GET", "/auth", headers=_auth_headers(token))
    return response.json()


def ensure_supported_table(table: str) -> None:
    if table not in _SUPPORTED_TABLES:
        raise ValueError(f"Unsupported table '{table}'. Supported tables: {sorted(_SUPPORTED_TABLES)}")


async def find_all(table: str, token: str, params: dict | None = None) -> list:
    ensure_supported_table(table)
    response = await _request(
        "GET", f"/data/{table}/", headers=_auth_headers(token), params=params or {}
    )
    return response.json()


async def find_one(table: str, item_id: str, token: str, params: dict | None = None) -> dict:
    ensure_supported_table(table)
    response = await _request(
        "GET", f"/data/{table}/{item_id}", headers=_auth_headers(token), params=params or {}
    )
    return response.json()


async def upload_single(item_id: str, token: str, file_bytes: bytes, filename: str, data_type: str) -> dict:
    files = {"file": (filename, file_bytes)}
    response = await _request(
        "POST",
        f"/data/upload/{item_id}",
        headers=_auth_headers(token),
        files=files,
        data={"type": data_type},
    )
    return response.json()


async def upload_multiple(item_id: str, token: str, uploads: list[dict]) -> dict:
    """`uploads` is a list of dicts: {filename, content, type, name, size, date}."""
    files = [("file", (u["filename"], u["content"])) for u in uploads]
    data = {
        "type": [u.get("type", "") for u in uploads],
        "name": [u.get("name", u["filename"]) for u in uploads],
        "size": [str(u.get("size", len(u["content"]))) for u in uploads],
        "date": [u.get("date", "") for u in uploads],
    }
    response = await _request(
        "POST", f"/data/uploads/{item_id}", headers=_auth_headers(token), files=files, data=data
    )
    return response.json()


async def query_projects(name: str, token: str) -> list[dict]:
    """Search Shigure projects by name/code/captain (see `GET /project/query/:name`)."""
    response = await _request("GET", f"/project/query/{name}", headers=_auth_headers(token))
    payload = response.json()
    return payload.get("data", []) if isinstance(payload, dict) else payload


async def download(table: str, item_id: str, token: str, data_type: str | None = None) -> httpx.Response:
    ensure_supported_table(table)
    response = await _request(
        "POST",
        f"/data/download/{table}/{item_id}",
        headers=_auth_headers(token),
        json={"type": data_type} if data_type else {},
    )
    return response

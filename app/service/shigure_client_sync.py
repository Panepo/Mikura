"""Synchronous Shigure API client for use inside worker threads / scheduler jobs
(APScheduler's BackgroundScheduler runs jobs in plain threads, not asyncio)."""
from typing import Any

import httpx

from app.core.config import get_settings

settings = get_settings()


class ShigureApiError(Exception):
    def __init__(self, status_code: int, detail: Any):
        self.status_code = status_code
        self.detail = detail
        super().__init__(f"Shigure API error {status_code}: {detail}")


def login(username: str, password: str) -> dict:
    url = f"{settings.shigure_api_base_url.rstrip('/')}/auth"
    with httpx.Client(timeout=30.0) as client:
        response = client.post(url, json={"username": username, "password": password})
    if response.status_code >= 400:
        try:
            detail = response.json()
        except ValueError:
            detail = response.text
        raise ShigureApiError(response.status_code, detail)
    return response.json()

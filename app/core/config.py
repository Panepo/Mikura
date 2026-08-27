"""Application configuration loaded from environment variables (.env)."""
import os
from functools import lru_cache

from dotenv import load_dotenv

load_dotenv()


def _split_csv(value: str) -> list[str]:
    return [item.strip() for item in value.split(",") if item.strip()]


class Settings:
    # Manager access control: Shigure user ids (the `sub`/`id` claim), not usernames.
    # Real Shigure JWTs carry no name/role claims, so this is the only reliable identity signal.
    managers: list[str] = _split_csv(os.getenv("MANAGERS", ""))

    # Shigure Data Center
    shigure_api_base_url: str = os.getenv("SHIGURE_API_BASE_URL", "http://localhost:4000")
    # Static bearer token used by Mikura to call Shigure's project search API on behalf of the server
    # and for unattended weekly builds
    shigure_token: str = os.getenv("SHIGURE_TOKEN", "")

    # Database
    database_url: str = os.getenv("DATABASE_URL", "sqlite+aiosqlite:///./mikura.db")
    sync_database_url: str = os.getenv("SYNC_DATABASE_URL", "sqlite:///./mikura.db")

    # Build / storage
    build_output_dir: str = os.getenv("BUILD_OUTPUT_DIR", "./builds")
    build_retention_count: int = int(os.getenv("BUILD_RETENTION_COUNT", "3"))

    # Weekly scheduler defaults (day_of_week: mon,tue,...; hour/minute 24h)
    weekly_build_day: str = os.getenv("WEEKLY_BUILD_DAY", "mon")
    weekly_build_hour: int = int(os.getenv("WEEKLY_BUILD_HOUR", "2"))
    weekly_build_minute: int = int(os.getenv("WEEKLY_BUILD_MINUTE", "0"))

    # Notification recipients for build failure / retention cleanup emails
    notify_emails: list[str] = _split_csv(os.getenv("NOTIFY_EMAILS", ""))

    def is_manager(self, username: str) -> bool:
        if not username:
            return False
        return username.lower() in {m.lower() for m in self.managers}


@lru_cache
def get_settings() -> Settings:
    return Settings()

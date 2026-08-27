"""Pydantic request/response schemas for the API."""
import datetime

from pydantic import BaseModel


class LoginRequest(BaseModel):
    username: str
    password: str


class ProjectCreate(BaseModel):
    name: str
    description: str = ""


class ShigureProjectResult(BaseModel):
    name: str
    code: str
    captain: str


class ProjectOut(BaseModel):
    id: int
    name: str
    description: str
    status: str

    model_config = {"from_attributes": True}


class ScheduleRequest(BaseModel):
    is_active: bool = True
    day_of_week: str = "mon"
    hour: int = 2
    minute: int = 0


class BuildHistoryOut(BaseModel):
    id: int
    build_status: str
    trigger: str
    started_at: datetime.datetime
    completed_at: datetime.datetime | None
    output_file_path: str | None
    ids_used: list[str]
    error_message: str | None

    model_config = {"from_attributes": True}


class BuildFileOut(BaseModel):
    id: int
    file_name: str
    file_path: str
    build_history_id: int
    created_at: datetime.datetime

    model_config = {"from_attributes": True}


class BuildTriggerResponse(BaseModel):
    build_history_id: int
    status: str

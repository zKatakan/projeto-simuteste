from __future__ import annotations
from typing import Optional, List
from datetime import date
from pydantic import BaseModel, field_validator

class UserIn(BaseModel):
    name: str
    email: str

class UserOut(UserIn):
    id: int

class ProjectIn(BaseModel):
    name: str
    description: str = ""

class ProjectOut(ProjectIn):
    id: int

class TaskIn(BaseModel):
    title: str
    description: str = ""
    status: str = "OPEN"
    priority: int = 3
    due_date: Optional[date] = None
    project_id: int
    assignee_id: Optional[int] = None
    tag_ids: List[int] = []

    @field_validator("priority")
    @classmethod
    def validate_priority(cls, v: int):
        if v < 1 or v > 5:
            raise ValueError("priority deve estar entre 1 e 5")
        return v

class TaskOut(BaseModel):
    id: int
    title: str
    description: str
    status: str
    priority: int
    due_date: Optional[date]
    project_id: int
    assignee_id: Optional[int]
    tags: List[str] = []

class TagIn(BaseModel):
    name: str

class TagOut(TagIn):
    id: int

class AttachmentOut(BaseModel):
    id: int
    task_id: int
    filename: str
    filepath: str

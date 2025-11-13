# app/models/entities.py
from __future__ import annotations
from typing import Optional
from datetime import datetime, date
from sqlmodel import SQLModel, Field

class User(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str
    email: str

class Project(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str
    description: str = ""

class Task(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    title: str
    description: str = ""
    status: str = "OPEN"   # OPEN, IN_PROGRESS, DONE
    priority: int = 3      # 1..5
    due_date: Optional[date] = None
    project_id: int = Field(foreign_key="project.id")
    assignee_id: Optional[int] = Field(default=None, foreign_key="user.id")

class Tag(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str

class TaskTagLink(SQLModel, table=True):
    task_id: Optional[int] = Field(default=None, foreign_key="task.id", primary_key=True)
    tag_id: Optional[int] = Field(default=None, foreign_key="tag.id", primary_key=True)

class Attachment(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    task_id: int = Field(foreign_key="task.id")
    filename: str
    filepath: str
    created_at: datetime = Field(default_factory=datetime.utcnow)

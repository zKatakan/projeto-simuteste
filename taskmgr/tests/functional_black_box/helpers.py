from dataclasses import dataclass
from datetime import date
from typing import Optional


@dataclass
class DummyTask:
    id: Optional[int] = None
    title: str = "Task"
    description: str = ""
    status: str = "OPEN"
    priority: int = 3
    due_date: Optional[date] = None
    project_id: Optional[int] = None
    assignee_id: Optional[int] = None


class FakeTaskRepo:
    """Repo fake em memória para testar regras de negócio."""

    def __init__(self, tasks=None, open_per_user=None):
        self.tasks = {t.id: t for t in (tasks or []) if t.id is not None}
        self.open_per_user = open_per_user or {}
        self.created = []
        self.updated = []

    def count_open_by_user(self, user_id: int) -> int:
        return self.open_per_user.get(user_id, 0)

    def create(self, data, tag_ids):
        new_id = (max(self.tasks.keys(), default=0) or 0) + 1
        data.id = new_id
        self.tasks[new_id] = data
        self.created.append((data, tuple(tag_ids or [])))
        return data

    def get(self, task_id: int):
        return self.tasks.get(task_id)

    def update_status(self, task_id: int, new_status: str):
        task = self.tasks[task_id]
        task.status = new_status
        self.updated.append((task_id, new_status))
        return task

    # usado pelo ProjectService
    def list_with_filters(self, project_id: int | None = None):
        if project_id is None:
            return list(self.tasks.values())
        return [t for t in self.tasks.values() if t.project_id == project_id]


class FakeProjectRepo:
    def __init__(self):
        self.archived = set()

    def archive(self, project_id: int):
        self.archived.add(project_id)

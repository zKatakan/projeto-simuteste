# app/repositories/task_repo.py
from typing import List, Optional
from sqlmodel import Session, select
from app.models.entities import Task, Tag, TaskTagLink

class TaskRepo:
    def __init__(self, session: Session):
        self.session = session

    def create(self, task: Task, tag_ids: List[int]) -> Task:
        self.session.add(task)
        self.session.flush()
        if tag_ids:
            for tid in tag_ids:
                self.session.add(TaskTagLink(task_id=task.id, tag_id=tid))
        self.session.commit()
        self.session.refresh(task)
        return task

    def get(self, task_id: int) -> Optional[Task]:
        return self.session.get(Task, task_id)

    def update_status(self, task_id: int, new_status: str) -> Task:
        task = self.get(task_id)
        task.status = new_status
        self.session.add(task)
        self.session.commit()
        self.session.refresh(task)
        return task

    def count_open_by_user(self, user_id: int) -> int:
        stmt = select(Task).where(Task.assignee_id == user_id, Task.status != "DONE")
        return len(self.session.exec(stmt).all())

    def list_with_filters(
        self,
        *,
            status: Optional[str]=None,
            project_id: Optional[int]=None,
            assignee_id: Optional[int]=None,
            tag: Optional[str]=None,
            q: Optional[str]=None,
            order_by: Optional[str]=None
    ) -> List[Task]:
        # base
        stmt = select(Task)
        if status:
            stmt = stmt.where(Task.status == status)
        if project_id:
            stmt = stmt.where(Task.project_id == project_id)
        if assignee_id is not None:
            stmt = stmt.where(Task.assignee_id == assignee_id)
        if q:
            stmt = stmt.where(Task.title.contains(q))
        if order_by in {"due_date", "priority"}:
            stmt = stmt.order_by(getattr(Task, order_by))

        # filtro por tag via join na tabela de ligação
        if tag:
            stmt = (
                select(Task)
                .join(TaskTagLink, TaskTagLink.task_id == Task.id)
                .join(Tag, Tag.id == TaskTagLink.tag_id)
                .where(Tag.name == tag)
            )
            if status:
                stmt = stmt.where(Task.status == status)
            if project_id:
                stmt = stmt.where(Task.project_id == project_id)
            if assignee_id is not None:
                stmt = stmt.where(Task.assignee_id == assignee_id)
            if q:
                stmt = stmt.where(Task.title.contains(q))
            if order_by in {"due_date", "priority"}:
                stmt = stmt.order_by(getattr(Task, order_by))

        return self.session.exec(stmt).all()

    # utilitário para montar lista de nomes de tags de uma task
    def tag_names_for_task(self, task_id: int) -> List[str]:
        stmt = (
            select(Tag.name)
            .join(TaskTagLink, TaskTagLink.tag_id == Tag.id)
            .where(TaskTagLink.task_id == task_id)
        )
        return [row[0] for row in self.session.exec(stmt)]

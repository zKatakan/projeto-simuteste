# app/api/v1/tasks.py
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session

from app.core.deps import get_session
from app.core.exceptions import http_error_from_domain, DomainError
from app.models.entities import Task
from app.models.schemas import TaskIn, TaskOut
from app.repositories.task_repo import TaskRepo
from app.services.task_service import TaskService

router = APIRouter()


@router.post("/tasks", response_model=TaskOut)
def create_task(payload: TaskIn, session: Session = Depends(get_session)):
    repo = TaskRepo(session)
    svc = TaskService(repo)
    try:
        task = Task(**payload.model_dump(exclude={"tag_ids"}))
        created = svc.create_task(task, payload.tag_ids)
        tag_names = repo.tag_names_for_task(created.id)
        return TaskOut(
            id=created.id,
            title=created.title,
            description=created.description,
            status=created.status,
            priority=created.priority,
            due_date=created.due_date,
            project_id=created.project_id,
            assignee_id=created.assignee_id,
            tags=tag_names,
        )
    except DomainError as e:
        raise http_error_from_domain(e)


@router.get("/tasks")
def list_tasks(
    status: Optional[str] = None,
    project_id: Optional[int] = None,
    assignee_id: Optional[int] = None,
    tag: Optional[str] = None,
    q: Optional[str] = None,
    order_by: Optional[str] = None,
    session: Session = Depends(get_session),
):
    repo = TaskRepo(session)
    tasks = repo.list_with_filters(
        status=status,
        project_id=project_id,
        assignee_id=assignee_id,
        tag=tag,
        q=q,
        order_by=order_by,
    )
    out = []
    for t in tasks:
        out.append(
            TaskOut(
                id=t.id,
                title=t.title,
                description=t.description,
                status=t.status,
                priority=t.priority,
                due_date=t.due_date,
                project_id=t.project_id,
                assignee_id=t.assignee_id,
                tags=repo.tag_names_for_task(t.id),
            )
        )
    return out


# 🔧 AJUSTE IMPORTANTE: caminho correto + uso do service
@router.patch("/tasks/{task_id}/status")
def update_status(task_id: int, new_status: str, session: Session = Depends(get_session)):
    """
    Atualiza o status da tarefa aplicando as regras de domínio:

    - 404 se a task não existir
    - 422 se tentar marcar DONE sem responsável (code='no_assignee')
    - 200 com {id, status} em caso de sucesso
    """
    repo = TaskRepo(session)
    svc = TaskService(repo)
    try:
        task = svc.update_status(task_id, new_status)
        return {"id": task.id, "status": task.status}
    except DomainError as e:
        # http_error_from_domain mapeia:
        # - ValidationError -> 422
        # - DomainError -> 400
        # - NotFoundError -> 404
        raise http_error_from_domain(e)

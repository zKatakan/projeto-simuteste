from datetime import date
from app.core.config import settings
from app.core.exceptions import DomainError, ValidationError, NotFoundError
from app.core.logging_config import logger  # 👈 novo import
from app.models.entities import Task
from app.repositories.task_repo import TaskRepo


class TaskService:
    def __init__(self, repo: TaskRepo):  # 👈 corrigido para __init__
        self.repo = repo

    def create_task(self, data: Task, tag_ids):
        logger.info(
            "Criando tarefa: title=%s, project_id=%s, assignee_id=%s, due_date=%s",
            data.title,
            data.project_id,
            data.assignee_id,
            data.due_date,
        )

        # Regra: data de vencimento não pode estar no passado
        if data.due_date and data.due_date < date.today():
            logger.warning(
                "Tentativa de criar tarefa com due_date no passado: title=%s, due_date=%s",
                data.title,
                data.due_date,
            )
            raise ValidationError(
                "due_date_past",
                "A data de vencimento não pode estar no passado.",
            )

        # Regra: limite de tarefas abertas por usuário
        if data.assignee_id is not None:
            open_count = self.repo.count_open_by_user(data.assignee_id)
            if open_count >= settings.MAX_OPEN_TASKS_PER_USER:
                logger.warning(
                    "User overload: usuário id=%s já possui %s tarefas abertas (limite=%s)",
                    data.assignee_id,
                    open_count,
                    settings.MAX_OPEN_TASKS_PER_USER,
                )
                raise DomainError(
                    "user_overload",
                    (
                        f"Usuário já possui {open_count} tarefas abertas "
                        f"(limite {settings.MAX_OPEN_TASKS_PER_USER})."
                    ),
                )

        task = self.repo.create(data, tag_ids)
        logger.info("Tarefa criada com sucesso: id=%s", task.id)
        return task

    def update_status(self, task_id: int, new_status: str) -> Task:
        logger.info(
            "Alterando status da task id=%s para %s",
            task_id,
            new_status,
        )

        task = self.repo.get(task_id)
        if not task:
            logger.error(
                "Tentativa de alterar status de task inexistente: id=%s",
                task_id,
            )
            raise NotFoundError("not_found", "Task inexistente.")

        # Regra: não pode DONE sem responsável
        if new_status == "DONE" and not task.assignee_id:
            logger.warning(
                "Regra violada: tentativa de concluir task id=%s com status DONE sem responsável",
                task.id,
            )
            raise ValidationError(
                "no_assignee",
                "Tarefa não pode ser concluída sem responsável.",
            )

        updated = self.repo.update_status(task_id, new_status)
        logger.info(
            "Status da task id=%s atualizado de %s para %s",
            updated.id,
            task.status,
            updated.status,
        )
        return updated

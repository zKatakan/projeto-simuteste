from types import SimpleNamespace
from typing import Iterable

from app.repositories.project_repo import ProjectRepo
from app.repositories.task_repo import TaskRepo
from app.core.logging_config import logger


class ProjectService:
    def __init__(self, projects: ProjectRepo, tasks: TaskRepo):
        self.projects = projects
        self.tasks = tasks

    def can_archive(self, project_id: int) -> bool:
        logger.info("Verificando se projeto id=%s pode ser arquivado", project_id)

        tasks = self.tasks.list_with_filters(project_id=project_id)

        blocking_tasks = [
            t for t in tasks
            if t.priority <= 2 and t.status != "DONE"
        ]

        if blocking_tasks:
            # Nem todo objeto de teste tem atributo id, então usamos getattr.
            ids = [getattr(t, "id", None) for t in blocking_tasks]
            logger.info(
                "Projeto %s NÃO pode ser arquivado; tarefas críticas ainda abertas: %s",
                project_id,
                ids,
            )
            return False

        logger.info("Projeto %s pode ser arquivado", project_id)
        return True

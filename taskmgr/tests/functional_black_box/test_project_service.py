import pytest

from app.services.project_service import ProjectService
from .helpers import DummyTask, FakeTaskRepo, FakeProjectRepo




def _make_project_service_with_tasks(tasks):
    task_repo = FakeTaskRepo(tasks=tasks)
    project_repo = FakeProjectRepo()
    service = ProjectService(projects=project_repo, tasks=task_repo)
    return service, project_repo, task_repo


def test_can_archive_quando_nao_tem_tarefas_retorna_true():
    service, _, _ = _make_project_service_with_tasks([])
    assert service.can_archive(project_id=1) is True


def test_can_archive_quando_todas_tarefas_sao_DONE_retorna_true():
    tasks = [
        DummyTask(id=1, project_id=1, status="DONE", priority=1),
        DummyTask(id=2, project_id=1, status="DONE", priority=2),
    ]
    service, _, _ = _make_project_service_with_tasks(tasks)
    assert service.can_archive(project_id=1) is True


def test_can_archive_ignora_tarefas_de_outro_projeto():
    tasks = [
        DummyTask(id=1, project_id=1, status="DONE", priority=1),
        DummyTask(id=2, project_id=2, status="OPEN", priority=1),
    ]
    service, _, _ = _make_project_service_with_tasks(tasks)
    assert service.can_archive(project_id=1) is True


def test_can_archive_bloqueia_quando_existe_tarefa_critica_nao_DONE():
    tasks = [
        DummyTask(id=1, project_id=1, status="DONE", priority=1),
        DummyTask(id=2, project_id=1, status="OPEN", priority=1),
    ]
    service, _, _ = _make_project_service_with_tasks(tasks)
    assert service.can_archive(project_id=1) is False


def test_can_archive_considera_prioridade_2_como_critica_se_nao_DONE():
    tasks = [
        DummyTask(id=1, project_id=1, status="IN_PROGRESS", priority=2),
    ]
    service, _, _ = _make_project_service_with_tasks(tasks)
    assert service.can_archive(project_id=1) is False


def test_can_archive_nao_bloqueia_prioridade_maior_que_2_aberta():
    tasks = [
        DummyTask(id=1, project_id=1, status="OPEN", priority=3),
        DummyTask(id=2, project_id=1, status="OPEN", priority=5),
    ]
    service, _, _ = _make_project_service_with_tasks(tasks)
    assert service.can_archive(project_id=1) is True


@pytest.mark.parametrize(
    "priority,status,esperado",
    [
        (1, "OPEN", False),
        (1, "DONE", True),
        (2, "IN_PROGRESS", False),
        (2, "DONE", True),
        (3, "OPEN", True),
        (3, "DONE", True),
    ],
)
def test_can_archive_casos_parametrizados(priority, status, esperado):
    tasks = [
        DummyTask(id=1, project_id=1, priority=priority, status=status),
    ]
    service, _, _ = _make_project_service_with_tasks(tasks)
    assert service.can_archive(project_id=1) is esperado

def test_can_archive_projeto_com_varias_tarefas_em_varios_projetos():
    # Projeto 1 só tem tarefas DONE
    # Outros projetos ainda têm tarefas críticas abertas, mas isso não deve bloquear o projeto 1
    tasks = [
        DummyTask(id=1, project_id=1, status="DONE", priority=1),
        DummyTask(id=2, project_id=1, status="DONE", priority=3),
        DummyTask(id=3, project_id=2, status="OPEN", priority=1),        # crítico, mas de outro projeto
        DummyTask(id=4, project_id=3, status="IN_PROGRESS", priority=2), # crítico, mas de outro projeto
    ]
    service, _, _ = _make_project_service_with_tasks(tasks)

    # Só queremos saber se o projeto 1 pode ser arquivado
    assert service.can_archive(project_id=1) is True


from datetime import date, timedelta

import pytest

from app.core.config import settings
from app.core.exceptions import DomainError, ValidationError, NotFoundError
from app.services.task_service import TaskService
from .helpers import DummyTask, FakeTaskRepo



# ========= create_task =========

def test_create_task_sem_due_date_e_sem_responsavel_ok(task_service, fake_task_repo):
    task = DummyTask(due_date=None, assignee_id=None)
    created = task_service.create_task(task, tag_ids=[1, 2])

    assert created.id is not None
    assert len(fake_task_repo.created) == 1
    saved_task, tag_ids = fake_task_repo.created[0]
    assert saved_task is task
    assert tag_ids == (1, 2)


def test_create_task_com_due_date_futura_ok(task_service, fake_task_repo, future_date):
    task = DummyTask(due_date=future_date, assignee_id=None)
    created = task_service.create_task(task, tag_ids=[])

    assert created.id is not None
    assert created.due_date == future_date


def test_create_task_com_due_date_hoje_ok(task_service, fake_task_repo, today):
    task = DummyTask(due_date=today, assignee_id=None)
    created = task_service.create_task(task, tag_ids=[])

    assert created.id is not None
    assert created.due_date == today


@pytest.mark.parametrize("days_before", [1, 10, 365])
def test_create_task_com_data_no_passado_dispara_erro(task_service, days_before):
    past = date.today() - timedelta(days=days_before)
    task = DummyTask(due_date=past, assignee_id=None)

    with pytest.raises(ValidationError) as exc:
        task_service.create_task(task, tag_ids=[])

    assert exc.value.code == "due_date_past"


def test_create_task_com_usuario_abaixo_do_limite_ok():
    fake_repo = FakeTaskRepo(open_per_user={1: 0})
    service = TaskService.__new__(TaskService)
    service.repo = fake_repo

    task = DummyTask(due_date=None, assignee_id=1)
    created = service.create_task(task, tag_ids=None)

    assert created.id is not None
    assert fake_repo.count_open_by_user(1) == 0


def test_create_task_com_usuario_no_limite_dispara_DomainError(overloaded_task_repo):
    service = TaskService.__new__(TaskService)
    service.repo = overloaded_task_repo

    task = DummyTask(due_date=None, assignee_id=1)

    with pytest.raises(DomainError) as exc:
        service.create_task(task, tag_ids=None)

    assert exc.value.code == "user_overload"
    assert str(settings.MAX_OPEN_TASKS_PER_USER) in exc.value.message


def test_create_task_sem_assignee_nao_checa_limite(fake_task_repo):
    called = {"value": False}

    def fake_count_open_by_user(user_id: int):
        called["value"] = True
        return 999

    fake_task_repo.count_open_by_user = fake_count_open_by_user  # type: ignore

    service = TaskService.__new__(TaskService)
    service.repo = fake_task_repo

    task = DummyTask(due_date=None, assignee_id=None)
    service.create_task(task, tag_ids=None)

    assert called["value"] is False


# ========= update_status =========

def _make_service_with_task(task: DummyTask):
    repo = FakeTaskRepo(tasks=[task])
    service = TaskService.__new__(TaskService)
    service.repo = repo
    return service, repo


def test_update_status_task_nao_encontrada_dispara_NotFoundError():
    repo = FakeTaskRepo(tasks=[])
    service = TaskService.__new__(TaskService)
    service.repo = repo

    with pytest.raises(NotFoundError) as exc:
        service.update_status(task_id=123, new_status="DONE")

    assert exc.value.code == "not_found"


def test_update_status_DONE_sem_responsavel_dispara_ValidationError():
    task = DummyTask(id=1, assignee_id=None, status="OPEN")
    service, _ = _make_service_with_task(task)

    with pytest.raises(ValidationError) as exc:
        service.update_status(task_id=1, new_status="DONE")

    assert exc.value.code == "no_assignee"


def test_update_status_DONE_com_responsavel_ok():
    task = DummyTask(id=1, assignee_id=10, status="IN_PROGRESS")
    service, repo = _make_service_with_task(task)

    updated = service.update_status(task_id=1, new_status="DONE")

    assert updated.status == "DONE"
    assert repo.updated == [(1, "DONE")]


def test_update_status_para_status_nao_DONE_sem_responsavel_permitido():
    task = DummyTask(id=1, assignee_id=None, status="OPEN")
    service, repo = _make_service_with_task(task)

    updated = service.update_status(task_id=1, new_status="IN_PROGRESS")

    assert updated.status == "IN_PROGRESS"
    assert repo.updated == [(1, "IN_PROGRESS")]


@pytest.mark.parametrize(
    "initial_status,new_status",
    [
        ("OPEN", "IN_PROGRESS"),
        ("IN_PROGRESS", "ON_HOLD"),
        ("ON_HOLD", "OPEN"),
    ],
)
def test_update_status_fluxos_varios_sem_quebrar_regra(initial_status, new_status):
    task = DummyTask(id=1, assignee_id=5, status=initial_status)
    service, repo = _make_service_with_task(task)

    updated = service.update_status(task_id=1, new_status=new_status)

    assert updated.status == new_status
    assert repo.updated[-1] == (1, new_status)


def test_update_status_nao_altera_outros_campos():
    task = DummyTask(
        id=1,
        assignee_id=5,
        status="OPEN",
        title="Titulo",
        description="Desc",
        priority=2,
    )
    service, _ = _make_service_with_task(task)

    before = task.__dict__.copy()
    updated = service.update_status(task_id=1, new_status="DONE")

    assert updated.title == before["title"]
    assert updated.description == before["description"]
    assert updated.priority == before["priority"]

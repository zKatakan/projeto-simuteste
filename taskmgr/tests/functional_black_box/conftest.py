import pytest
from datetime import date, timedelta

from app.core.config import settings
from app.services.task_service import TaskService
from app.services.project_service import ProjectService

# tests/functional_black_box/conftest.py

from .helpers import DummyTask, FakeTaskRepo, FakeProjectRepo



@pytest.fixture
def today():
    return date.today()


@pytest.fixture
def past_date(today):
    return today - timedelta(days=1)


@pytest.fixture
def future_date(today):
    return today + timedelta(days=1)


@pytest.fixture
def fake_task_repo():
    return FakeTaskRepo()


@pytest.fixture
def overloaded_task_repo():
    return FakeTaskRepo(open_per_user={1: settings.MAX_OPEN_TASKS_PER_USER})


@pytest.fixture
def task_service(fake_task_repo):
    service = TaskService.__new__(TaskService)
    service.repo = fake_task_repo
    return service


@pytest.fixture
def project_service():
    task_repo = FakeTaskRepo()
    project_repo = FakeProjectRepo()
    service = ProjectService(projects=project_repo, tasks=task_repo)
    return service, project_repo, task_repo, DummyTask

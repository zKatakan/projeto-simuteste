import pytest
from datetime import date, timedelta
from types import SimpleNamespace
from app.services.task_service import TaskService
from app.core.exceptions import DomainError, ValidationError

class MockRepo:
    def __init__(self, open_by_user=0):
        self.open_by_user = open_by_user
    def count_open_by_user(self, uid):
        return self.open_by_user
    def create(self, data, tag_ids):
        data.id = 1
        return data
    def get(self, task_id):
        return SimpleNamespace(id=task_id, assignee_id=1, status="OPEN")
    def update_status(self, task_id, new_status):
        return SimpleNamespace(id=task_id, status=new_status)

@pytest.mark.parametrize("days_offset,expect_error", [(-1, True), (0, False), (5, False), (-10, True)])
def test_due_date_validation(days_offset, expect_error):
    repo = MockRepo(open_by_user=0)
    svc = TaskService(repo)
    data = SimpleNamespace(title="x", description="", status="OPEN", priority=3,
                           due_date=date.today()+timedelta(days=days_offset), project_id=1, assignee_id=None)
    if expect_error:
        with pytest.raises(ValidationError):
            svc.create_task(data, [])
    else:
        created = svc.create_task(data, [])
        assert created.title == "x"

@pytest.mark.parametrize(
    "open_count,should_block",
    [
        (0, False),  # nenhum aberto → pode criar
        (1, True),   # já tem 1 aberto → deve bloquear
        (2, True),   # 2 abertos → continua bloqueando
        (5, True),   # vários abertos → bloqueia também
    ],
)
def test_user_overload(open_count, should_block):
    svc = TaskService(MockRepo(open_by_user=open_count))
    data = SimpleNamespace(
        title="x",
        description="",
        status="OPEN",
        priority=3,
        due_date=None,
        project_id=1,
        assignee_id=123,
    )
    if should_block:
        with pytest.raises(DomainError):
            svc.create_task(data, [])
    else:
        assert svc.create_task(data, []).title == "x"


def test_update_status_requires_assignee_for_done():
    svc = TaskService(MockRepo())
    svc.repo.get = lambda _id: SimpleNamespace(id=_id, assignee_id=None, status="IN_PROGRESS")
    with pytest.raises(ValidationError):
        svc.update_status(1, "DONE")

def test_update_status_ok():
    svc = TaskService(MockRepo())
    out = svc.update_status(1, "IN_PROGRESS")
    assert out.status == "IN_PROGRESS"

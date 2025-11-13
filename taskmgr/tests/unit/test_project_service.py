from types import SimpleNamespace
from app.services.project_service import ProjectService

class TRepo:
    def __init__(self, tasks):
        self._tasks = tasks
    def list_with_filters(self, **kwargs):
        return self._tasks

def test_can_archive_true():
    svc = ProjectService(projects=None, tasks=TRepo(tasks=[SimpleNamespace(priority=5, status="DONE")]))
    assert svc.can_archive(1) is True

def test_can_archive_false_high_priority_open():
    svc = ProjectService(projects=None, tasks=TRepo(tasks=[SimpleNamespace(priority=1, status="OPEN")]))
    assert svc.can_archive(1) is False

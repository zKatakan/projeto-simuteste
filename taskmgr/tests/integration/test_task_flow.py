from sqlmodel import Session
from app.models.db import create_db_and_tables, engine
from app.models.entities import Project, Task
from app.repositories.project_repo import ProjectRepo
from app.repositories.task_repo import TaskRepo

def test_task_filters_and_order():
    create_db_and_tables()
    with Session(engine) as s:
        pr = ProjectRepo(s)
        tr = TaskRepo(s)
        p = pr.create(Project(name="P"))
        tr.create(Task(title="A", project_id=p.id, priority=2), [])
        tr.create(Task(title="B", project_id=p.id, priority=5), [])
        lst = tr.list_with_filters(project_id=p.id, order_by="priority")
        assert [t.title for t in lst] == ["A", "B"]

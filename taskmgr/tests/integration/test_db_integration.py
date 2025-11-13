from sqlmodel import Session
from app.models.db import create_db_and_tables, engine
from app.models.entities import Project, User, Task
from app.repositories.project_repo import ProjectRepo
from app.repositories.user_repo import UserRepo
from app.repositories.task_repo import TaskRepo

def test_full_integration_simple():
    create_db_and_tables()
    with Session(engine) as s:
        pr = ProjectRepo(s)
        ur = UserRepo(s)
        tr = TaskRepo(s)
        p = pr.create(Project(name="P1"))
        u = ur.create(User(name="Ana", email="ana@x.com"))
        t = tr.create(Task(title="T1", project_id=p.id, assignee_id=u.id), [])
        assert t.id is not None
        assert pr.progress(p.id) in (0.0, 100.0)

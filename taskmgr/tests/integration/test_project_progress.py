from sqlmodel import Session
from app.models.db import create_db_and_tables, engine
from app.models.entities import Project, Task
from app.repositories.project_repo import ProjectRepo
from app.repositories.task_repo import TaskRepo

def test_progress_calc():
    create_db_and_tables()
    with Session(engine) as s:
        pr = ProjectRepo(s)
        tr = TaskRepo(s)
        p = pr.create(Project(name="P"))
        tr.create(Task(title="t1", project_id=p.id, status="DONE"), [])
        tr.create(Task(title="t2", project_id=p.id, status="OPEN"), [])
        assert pr.progress(p.id) == 50.0

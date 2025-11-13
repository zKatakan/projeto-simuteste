from typing import Optional, List
from sqlmodel import Session, select
from app.models.entities import Project, Task

class ProjectRepo:
    def __init__(self, session: Session):
        self.session = session

    def create(self, p: Project) -> Project:
        self.session.add(p)
        self.session.commit()
        self.session.refresh(p)
        return p

    def get(self, project_id: int) -> Optional[Project]:
        return self.session.get(Project, project_id)

    def list(self) -> List[Project]:
        return self.session.exec(select(Project)).all()

    def progress(self, project_id: int) -> float:
        tasks = self.session.exec(select(Task).where(Task.project_id == project_id)).all()
        if not tasks:
            return 0.0
        done = sum(1 for t in tasks if t.status == "DONE")
        return round((done / len(tasks)) * 100.0, 2)

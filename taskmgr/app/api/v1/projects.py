from fastapi import APIRouter, Depends
from sqlmodel import Session
from app.core.deps import get_session
from app.models.entities import Project
from app.models.schemas import ProjectIn, ProjectOut
from app.repositories.project_repo import ProjectRepo
from app.repositories.task_repo import TaskRepo
from app.services.project_service import ProjectService

router = APIRouter()

@router.post("/projects", response_model=ProjectOut)
def create_project(payload: ProjectIn, session: Session = Depends(get_session)):
    return ProjectRepo(session).create(Project(**payload.model_dump()))

@router.get("/projects/{project_id}/progress")
def project_progress(project_id: int, session: Session = Depends(get_session)):
    return {"progress": ProjectRepo(session).progress(project_id)}

@router.get("/projects/{project_id}/can-archive")
def can_archive(project_id: int, session: Session = Depends(get_session)):
    svc = ProjectService(ProjectRepo(session), TaskRepo(session))
    return {"can_archive": svc.can_archive(project_id)}

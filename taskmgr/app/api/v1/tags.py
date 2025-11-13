from fastapi import APIRouter, Depends
from sqlmodel import Session
from app.core.deps import get_session
from app.models.entities import Tag
from app.models.schemas import TagIn, TagOut
from app.repositories.tag_repo import TagRepo

router = APIRouter()

@router.post("/tags", response_model=TagOut)
def create_tag(payload: TagIn, session: Session = Depends(get_session)):
    return TagRepo(session).create(Tag(**payload.model_dump()))

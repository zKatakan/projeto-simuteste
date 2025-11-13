from fastapi import APIRouter, Depends
from sqlmodel import Session
from app.core.deps import get_session
from app.models.entities import User
from app.models.schemas import UserIn, UserOut
from app.repositories.user_repo import UserRepo

router = APIRouter()

@router.post("/users", response_model=UserOut)
def create_user(payload: UserIn, session: Session = Depends(get_session)):
    return UserRepo(session).create(User(**payload.model_dump()))

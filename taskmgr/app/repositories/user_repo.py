from typing import Optional, List
from sqlmodel import Session, select
from app.models.entities import User

class UserRepo:
    def __init__(self, session: Session):
        self.session = session

    def create(self, u: User) -> User:
        self.session.add(u)
        self.session.commit()
        self.session.refresh(u)
        return u

    def get(self, user_id: int) -> Optional[User]:
        return self.session.get(User, user_id)

    def list(self) -> List[User]:
        return self.session.exec(select(User)).all()

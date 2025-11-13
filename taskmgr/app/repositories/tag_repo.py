from typing import Optional, List
from sqlmodel import Session, select
from app.models.entities import Tag

class TagRepo:
    def __init__(self, session: Session):
        self.session = session

    def create(self, t: Tag) -> Tag:
        self.session.add(t)
        self.session.commit()
        self.session.refresh(t)
        return t

    def get(self, tag_id: int) -> Optional[Tag]:
        return self.session.get(Tag, tag_id)

    def list(self) -> List[Tag]:
        return self.session.exec(select(Tag)).all()

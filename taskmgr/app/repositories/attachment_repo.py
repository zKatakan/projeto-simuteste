from typing import Optional, List
from sqlmodel import Session, select
from app.models.entities import Attachment

class AttachmentRepo:
    def __init__(self, session: Session):
        self.session = session

    def create(self, a: Attachment) -> Attachment:
        self.session.add(a)
        self.session.commit()
        self.session.refresh(a)
        return a

    def get(self, attachment_id: int) -> Optional[Attachment]:
        return self.session.get(Attachment, attachment_id)

    def list_by_task(self, task_id: int) -> List[Attachment]:
        return self.session.exec(select(Attachment).where(Attachment.task_id == task_id)).all()

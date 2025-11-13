import os
from fastapi import UploadFile
from app.models.entities import Attachment
from app.repositories.attachment_repo import AttachmentRepo
from app.core.config import settings

class AttachmentService:
    def __init__(self, repo: AttachmentRepo):
        self.repo = repo
        os.makedirs(settings.FILE_STORAGE_DIR, exist_ok=True)

    async def save(self, task_id: int, file: UploadFile) -> Attachment:
        dest = os.path.join(settings.FILE_STORAGE_DIR, file.filename)
        with open(dest, "wb") as f:
            f.write(await file.read())
        a = Attachment(task_id=task_id, filename=file.filename, filepath=dest)
        return self.repo.create(a)

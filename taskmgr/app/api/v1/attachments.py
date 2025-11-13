from fastapi import APIRouter, Depends, UploadFile, File
from sqlmodel import Session
from app.core.deps import get_session
from app.services.attachment_service import AttachmentService
from app.repositories.attachment_repo import AttachmentRepo

router = APIRouter()

@router.post("/attachments")
async def upload_attachment(task_id: int, file: UploadFile = File(...), session: Session = Depends(get_session)):
    svc = AttachmentService(AttachmentRepo(session))
    a = await svc.save(task_id, file)
    return {"id": a.id, "task_id": a.task_id, "filename": a.filename, "filepath": a.filepath}

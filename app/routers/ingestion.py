# routers/ingestion.py
from fastapi import APIRouter, UploadFile, Depends, Request
from app.services.vector_service import process_file
from sqlalchemy.orm import Session
from app.db.database import get_db

router = APIRouter(prefix="/ingestion", tags=["Ingestion"])

@router.post("/upload")
async def upload_docs(request: Request, file: UploadFile, db: Session = Depends(get_db)):
    tenant_id = getattr(request.state, "tenant_id", None)
    content = await file.read()
    process_file(content, tenant_id)
    return {"msg": "File processed"}

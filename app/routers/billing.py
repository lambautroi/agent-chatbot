# routers/billing.py
from fastapi import APIRouter, Request, Depends
from sqlalchemy.orm import Session
from app.db.database import get_db
from app.db import models

router = APIRouter(prefix="/billing", tags=["Billing"])

@router.get("/usage")
def get_usage(request: Request, db: Session = Depends(get_db)):
    tenant_id = getattr(request.state, "tenant_id", None)
    messages = db.query(models.ChatMessage).filter_by(tenant_id=tenant_id).count()
    return {"tenant_id": tenant_id, "messages": messages}

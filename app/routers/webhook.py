from fastapi import APIRouter, Request, Depends
from sqlalchemy.orm import Session
from app.db import models
from app.db.database import get_db
from app.services.tenant_service import handle_incoming_message

router = APIRouter(prefix="/webhook", tags=["Webhook"])

@router.post("/{platform}")
async def receive_message(platform: str, request: Request):
    data = await request.json()
    await handle_incoming_message(platform, data)
    return {"status": "ok"}


@router.post("/webhook")
def webhook_handler(data: dict, db: Session = Depends(get_db)):
    conv_id = data.get("conversation_id")
    conv = db.query(models.Conversation).filter(models.Conversation.id == conv_id).first()
    if not conv or conv.mode == "bot":
        # Gọi GPT xử lý
        pass
    elif conv.mode == "human":
        # Đẩy tin nhắn tới dashboard agent qua WebSocket
        pass
    return {"msg": "ok"}
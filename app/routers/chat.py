from fastapi import APIRouter, Depends, HTTPException, Request, Body, WebSocket
from sqlalchemy.orm import Session
from datetime import datetime
from typing import List
from app.db import models
from app.db.database import get_db
from app.core.security import get_current_user
from app.services.llm_service import call_gpt
from app.websocket.manager import ConnectionManager
import json

router = APIRouter(prefix="/chat", tags=["Chat"])
manager = ConnectionManager()

# 1️⃣ Lấy danh sách hội thoại đang hoạt động
@router.get("/conversations")
def list_conversations(db: Session = Depends(get_db), user=Depends(get_current_user)):
    tenant_id = user.tenant_id
    if not tenant_id:
        raise HTTPException(status_code=403, detail="Tenant not found")
    conversations = (
        db.query(models.Conversation)
        .filter(models.Conversation.tenant_id == tenant_id)
        .order_by(models.Conversation.updated_at.desc())
        .all()
    )
    return conversations

# 2️⃣ Lấy chi tiết hội thoại + tin nhắn
@router.get("/conversations/{conversation_id}")
def get_conversation(conversation_id: int, db: Session = Depends(get_db), user=Depends(get_current_user)):
    convo = db.query(models.Conversation).filter_by(id=conversation_id, tenant_id=user.tenant_id).first()
    if not convo:
        raise HTTPException(status_code=404, detail="Conversation not found")
    messages = (
        db.query(models.Message)
        .filter(models.Message.conversation_id == conversation_id)
        .order_by(models.Message.timestamp.asc())
        .all()
    )
    return {"conversation": convo, "messages": messages}

# 3️⃣ Takeover: Chuyển sang mode "human"
@router.post("/conversations/{conversation_id}/takeover")
def takeover_conversation(conversation_id: int, db: Session = Depends(get_db), user=Depends(get_current_user)):
    convo = db.query(models.Conversation).filter_by(id=conversation_id, tenant_id=user.tenant_id).first()
    if not convo:
        raise HTTPException(status_code=404, detail="Conversation not found")
    convo.mode = "human"
    convo.active_agent_id = user.id
    convo.updated_at = datetime.utcnow()
    db.commit()
    return {"message": f"Conversation {conversation_id} taken over by {user.username}"}

# 4️⃣ Release: Trả lại quyền cho bot
@router.post("/conversations/{conversation_id}/release")
def release_conversation(conversation_id: int, db: Session = Depends(get_db), user=Depends(get_current_user)):
    convo = db.query(models.Conversation).filter_by(id=conversation_id, tenant_id=user.tenant_id).first()
    if not convo:
        raise HTTPException(status_code=404, detail="Conversation not found")
    convo.mode = "bot"
    convo.active_agent_id = None
    convo.updated_at = datetime.utcnow()
    db.commit()
    return {"message": f"Conversation {conversation_id} returned to bot mode"}

# 5️⃣ Gửi tin nhắn thủ công (agent → khách hàng)
@router.post("/send")
def send_manual_message(
    payload: dict = Body(...),
    db: Session = Depends(get_db),
    user=Depends(get_current_user)
):
    """
    payload = {
        "conversation_id": int,
        "content": str
    }
    """
    convo = db.query(models.Conversation).filter_by(id=payload["conversation_id"], tenant_id=user.tenant_id).first()
    if not convo:
        raise HTTPException(status_code=404, detail="Conversation not found")
    # Lưu tin nhắn
    msg = models.Message(
        conversation_id=convo.id,
        sender="agent",
        text=payload["content"],
        timestamp=datetime.utcnow()
    )
    db.add(msg)
    db.commit()
    # Gửi message tới người dùng qua nền tảng tích hợp (Zalo/Messenger)
    # (Giả định có service riêng, ví dụ: zalo_service.send_message_to_user)
    try:
        from app.services.zalo_service import send_message_to_user
        customer = db.query(models.Customer).filter_by(id=convo.customer_id).first()
        if customer:
            send_message_to_user(customer.phone, payload["content"], tenant_id=user.tenant_id)
    except Exception as e:
        print("Send message error:", e)
    return {"message": "Message sent successfully", "mode": convo.mode}

@router.post("/message")
def chat_with_bot(request: Request, message: str, db: Session = Depends(get_db)):
    tenant_id = getattr(request.state, "tenant_id", None)
    if not tenant_id:
        return {"error": "Missing tenant context"}

    # Gọi GPT
    reply = call_gpt(message)

    # Lưu hội thoại
    msg = models.ChatMessage(
        tenant_id=tenant_id, sender="customer", message=message
    )
    reply_msg = models.ChatMessage(
        tenant_id=tenant_id, sender="bot", message=reply
    )
    db.add_all([msg, reply_msg])
    db.commit()
    return {"reply": reply}

@router.websocket("/{conversation_id}")
async def websocket_endpoint(websocket: WebSocket, conversation_id: int, db: Session = Depends(get_db)):
    await manager.connect(conversation_id, websocket)
    try:
        while True:
            data = await websocket.receive_text()
            msg = json.loads(data)

            # Validate message
            sender = msg.get("sender", "agent")
            content = msg.get("content", "")

            if not content.strip():
                continue

            # Save to DB
            chat_message = models.ChatMessage(
                conversation_id=conversation_id,
                sender_role=models.SenderRole(sender),
                content=content,
                created_at=datetime.utcnow()
            )
            db.add(chat_message)
            db.commit()

            # Broadcast message to all clients in same conversation
            await manager.broadcast(conversation_id, {
                "sender": sender,
                "content": content,
                "timestamp": chat_message.created_at.isoformat()
            })

    except Exception as e:
        print(f"WebSocket error: {e}")
    finally:
        manager.disconnect(conversation_id, websocket)

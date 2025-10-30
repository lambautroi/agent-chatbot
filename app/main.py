from app.middleware.tenant_middleware import TenantMiddleware
from fastapi import FastAPI
from app.routers import auth, chat, webhook, ingestion, billing

app = FastAPI(title="Chatbot SaaS Backend")

app.add_middleware(TenantMiddleware)

app.include_router(auth.router)
app.include_router(chat.router)
app.include_router(webhook.router)
app.include_router(ingestion.router)
app.include_router(billing.router)

@app.get("/")
async def root():
    return {"message": "Chat WebSocket API đang chạy ngon lành"}

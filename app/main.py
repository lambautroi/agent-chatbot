from app.middleware.tenant_middleware import TenantMiddleware
from fastapi import FastAPI
from app.middleware.tenant_middleware import tenant_middleware
from app.routers import auth, chat, webhook, ingestion, billing

app = FastAPI(title="Chatbot SaaS Backend")

app.middleware("http")(tenant_middleware)
app.add_middleware(TenantMiddleware)

app.include_router(auth.router)
app.include_router(chat.router)
app.include_router(webhook.router)
app.include_router(ingestion.router)
app.include_router(billing.router)

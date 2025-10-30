from fastapi import Request, HTTPException
from jose import jwt, JWTError
from app.core.security import SECRET_KEY, ALGORITHM
from starlette.middleware.base import BaseHTTPMiddleware

class TenantMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        tenant_id = request.headers.get("X-Tenant-ID")
        if not tenant_id:
            raise HTTPException(status_code=400, detail="Tenant ID missing")
        request.state.tenant_id = int(tenant_id)
        response = await call_next(request)
        return response

    async def tenant_middleware(request: Request, call_next):
        auth = request.headers.get("Authorization")
        if auth and auth.startswith("Bearer "):
            token = auth.split(" ")[1]
            try:
                payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
                request.state.tenant_id = payload.get("tenant_id")
            except JWTError:
                request.state.tenant_id = None
        else:
            request.state.tenant_id = None
        response = await call_next(request)
        return response

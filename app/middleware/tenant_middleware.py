from fastapi import Request
from jose import jwt, JWTError
from app.core.security import SECRET_KEY, ALGORITHM

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

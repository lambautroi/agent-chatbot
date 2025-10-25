from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.db import models
from app.db.database import get_db
from app.core.security import verify_password, get_password_hash, create_access_token

router = APIRouter(prefix="/auth", tags=["Auth"])

@router.post("/register")
def register(username: str, password: str, tenant_name: str, db: Session = Depends(get_db)):
    tenant = models.Tenant(name=tenant_name)
    db.add(tenant)
    db.commit()
    db.refresh(tenant)

    hashed_pw = get_password_hash(password)
    user = models.User(username=username, hashed_password=hashed_pw, tenant_id=tenant.id)
    db.add(user)
    db.commit()
    return {"msg": "User registered", "tenant_id": tenant.id}

@router.post("/login")
def login(username: str, password: str, db: Session = Depends(get_db)):
    user = db.query(models.User).filter(models.User.username == username).first()
    if not user or not verify_password(password, user.hashed_password):
        raise HTTPException(status_code=401, detail="Invalid credentials")
    token = create_access_token({"sub": user.username, "tenant_id": user.tenant_id})
    return {"access_token": token, "token_type": "bearer"}
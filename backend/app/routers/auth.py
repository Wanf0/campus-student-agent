import hashlib

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from ..db import get_db
from ..models import User
from ..schemas import RegisterRequest, LoginRequest, AuthResponse

router = APIRouter(prefix="/auth", tags=["认证"])


def _hash(password: str) -> str:
    return hashlib.sha256(password.encode("utf-8")).hexdigest()


@router.post("/register", response_model=AuthResponse)
def register(req: RegisterRequest, db: Session = Depends(get_db)):
    exists = db.query(User).filter(User.username == req.username).first()
    if exists:
        raise HTTPException(status_code=400, detail="用户名已存在")
    user = User(
        username=req.username,
        password=_hash(req.password),
        name=req.name,
        role="student",
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return AuthResponse(user_id=user.id, username=user.username, role=user.role)


@router.post("/login", response_model=AuthResponse)
def login(req: LoginRequest, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.username == req.username).first()
    if not user or user.password != _hash(req.password):
        raise HTTPException(status_code=401, detail="用户名或密码错误")
    return AuthResponse(user_id=user.id, username=user.username, role=user.role)

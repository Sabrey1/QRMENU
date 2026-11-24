from datetime import datetime, timedelta, timezone

import jwt
from fastapi import HTTPException, status
from jwt import InvalidTokenError
from pwdlib import PasswordHash
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.config import settings
from app.models.users import User
from app.schemas.auth import RegisterRequest
from app.schemas.tenants import TenantCreate
from app.services.tenants import add_for_owner

password_hash = PasswordHash.recommended()


def register(db: Session, data: RegisterRequest):
    if db.scalar(select(User).where(User.email == data.email)):
        raise HTTPException(status_code=409, detail="Email is already registered")
    hashed_password = password_hash.hash(data.password.get_secret_value())
    # A concurrent registration can claim the same generated slug. Restart the
    # whole transaction so the next attempt sees it and chooses another one.
    for attempt in range(3):
        user = User(name=data.name, email=data.email, password_hash=hashed_password, is_active=True)
        db.add(user)
        try:
            db.flush()
            tenant = add_for_owner(db, TenantCreate(name=data.name, currency_code=data.currency_code), user)
            db.flush()
            db.commit()
            db.refresh(user)
            db.refresh(tenant)
            return user, tenant
        except IntegrityError as exc:
            db.rollback()
            if db.scalar(select(User.id).where(User.email == data.email)):
                raise HTTPException(status_code=409, detail="Email is already registered") from exc
            db.rollback()
            if attempt == 2:
                raise HTTPException(status_code=409, detail="Could not reserve a shop address. Please try again.") from exc
        except Exception:
            db.rollback()
            raise


def login(db: Session, email: str, password: str) -> str:
    user = db.scalar(select(User).where(User.email == email))
    if not user or not user.is_active or not password_hash.verify(password, user.password_hash):
        raise HTTPException(status_code=401, detail="Invalid email or password", headers={"WWW-Authenticate": "Bearer"})
    if len(settings.secret_key) < 32:
        raise HTTPException(status_code=503, detail="Authentication signing key is not configured")
    now = datetime.now(timezone.utc)
    return jwt.encode({"sub": str(user.id), "iat": now, "exp": now + timedelta(minutes=settings.access_token_expire_minutes)}, settings.secret_key, algorithm="HS256")


def user_from_token(db: Session, token: str) -> User:
    if len(settings.secret_key) < 32:
        raise HTTPException(status_code=503, detail="Authentication signing key is not configured")
    try:
        payload = jwt.decode(token, settings.secret_key, algorithms=["HS256"], options={"require": ["sub", "iat", "exp"]})
        user_id = int(payload["sub"])
    except (InvalidTokenError, ValueError, TypeError) as exc:
        raise HTTPException(status_code=401, detail="Invalid or expired token", headers={"WWW-Authenticate": "Bearer"}) from exc
    user = db.get(User, user_id)
    if not user or not user.is_active:
        raise HTTPException(status_code=401, detail="Invalid or expired token", headers={"WWW-Authenticate": "Bearer"})
    return user

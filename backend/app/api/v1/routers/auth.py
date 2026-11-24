from fastapi import APIRouter, status

from app.dependencies import CurrentUser, Db
from app.schemas.auth import LoginRequest, RegisterRequest, RegisterResponse, Token
from app.schemas.users import UserRead
from app.services import auth

router = APIRouter(prefix="/api/auth", tags=["Authentication"])


@router.post("/register", response_model=RegisterResponse, status_code=status.HTTP_201_CREATED)
def register(data: RegisterRequest, db: Db):
    user, tenant = auth.register(db, data)
    return RegisterResponse(**UserRead.model_validate(user).model_dump(), tenant=tenant)


@router.post("/login", response_model=Token)
def login(data: LoginRequest, db: Db):
    return Token(access_token=auth.login(db, data.email, data.password.get_secret_value()))


@router.get("/me", response_model=UserRead)
def me(user: CurrentUser):
    return user

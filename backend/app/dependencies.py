from typing import Annotated

from fastapi import Depends, HTTPException
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.users import User
from app.services.auth import user_from_token

Db = Annotated[Session, Depends(get_db)]
bearer = HTTPBearer(auto_error=False)


def get_current_user(db: Db, credentials: Annotated[HTTPAuthorizationCredentials | None, Depends(bearer)]) -> User:
    if credentials is None:
        raise HTTPException(status_code=401, detail="Authentication required", headers={"WWW-Authenticate": "Bearer"})
    return user_from_token(db, credentials.credentials)


CurrentUser = Annotated[User, Depends(get_current_user)]

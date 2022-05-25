"""API for the users (Not fully Implemented Yet)."""

import time
from typing import Optional

import jwt
from fastapi import APIRouter, Depends, Header, HTTPException
from fastapi import status as status_code
from fastapi.security import OAuth2PasswordBearer
from tmtrkr import models, settings
from tmtrkr.api import schemas

api = APIRouter()


def get_username(
    x_forwarded_user: Optional[str] = Header(default=None),
    token: Optional[str] = Depends(OAuth2PasswordBearer(tokenUrl="", auto_error=False)),
) -> Optional[str]:
    """Get username from trusted header or JWT token."""
    if settings.AUTH_USERS_ALLOW_XFORWARDED and x_forwarded_user:
        return x_forwarded_user.strip()
    if settings.AUTH_USERS_ALLOW_JWT and token:
        return get_username_from_token(token)
    return None


def get_username_from_token(token: str) -> Optional[str]:
    """Parse JWT token and get username."""
    try:
        payload = jwt.decode(token, key=settings.SECRET_KEY, algorithms=["HS256"])
        token = schemas.TokenData(**payload)
        return token.username
    except Exception as x:
        print("invalid token", x)
    return None


def create_token(user: models.User) -> str:
    """Create active JWT token for the user."""
    token = schemas.TokenData(
        username=user.name,
        userid=user.id,
        expire=int(time.time() + settings.AUTH_USERS_ALLOW_JWT_TTL),
    )
    return jwt.encode(token.dict(), key=settings.SECRET_KEY, algorithm="HS256")


def get_user(
    username=Depends(get_username),
    db=Depends(models.db_session),
) -> Optional[models.User]:
    """
    Get user -- from auth token or trusted headers.

    - creates a new user if username is unknown and AUTH_USERS_AUTO_CREATE
    - returns None if username is not set and AUTH_USERS_ALLOW_UNKNOWN
    """
    user = None
    if username:
        if settings.AUTH_USERS_AUTO_CREATE:
            user = models.User.get_or_create(db, name=username)
        else:
            user = models.User.first(db, name=username)
    if not user and not settings.AUTH_USERS_ALLOW_UNKNOWN:
        # user is not found and guests are not allowed
        raise HTTPException(status_code=status_code.HTTP_401_UNAUTHORIZED)
    return user


@api.get("/", response_model=schemas.UserList)
async def get_users(db=Depends(models.db_session)) -> schemas.UserList:
    """List all users."""
    users = models.User.all(db)
    return {"users": (u.as_dict() for u in users)}


@api.get("/login")
async def login():
    """Log in user."""
    raise HTTPException(status_code=status_code.HTTP_501_NOT_IMPLEMENTED)


@api.get("/logout")
async def logout():
    """Log out user."""
    raise HTTPException(status_code=status_code.HTTP_501_NOT_IMPLEMENTED)


@api.get("/token", response_model=schemas.TokenResponse)
async def token(user=Depends(get_user)) -> schemas.TokenResponse:
    """Create auth token for logged-in user."""
    token = create_token(user)
    return {"token": token}

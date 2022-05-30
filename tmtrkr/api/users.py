"""API for the users (Not fully Implemented Yet)."""

import json
import time
from typing import Optional
from urllib import parse, request

import jwt
from fastapi import APIRouter, Cookie, Depends, Header, HTTPException
from fastapi import status as status_code
from fastapi.responses import RedirectResponse
from fastapi.security import OAuth2PasswordBearer
from tmtrkr import models, settings
from tmtrkr.api import schemas

__all__ = ["api", "get_user"]


api = APIRouter()


def get_username(
    x_user: Optional[str] = Header(alias="x-forwarded-user", default=None),
    auth_token: Optional[str] = Depends(OAuth2PasswordBearer(tokenUrl="", auto_error=False)),
    cookie_token: Optional[str] = Cookie(alias="token", default=None),
) -> Optional[str]:
    """Get username from trusted header or JWT token."""
    if settings.AUTH_USERS_ALLOW_XFORWARDED and x_user:
        return x_user.strip()
    if settings.AUTH_USERS_ALLOW_JWT and auth_token:
        return get_username_from_token(auth_token)
    if settings.AUTH_USERS_ALLOW_JWT and cookie_token:
        return get_username_from_token(cookie_token)
    return None


def get_username_from_token(token: str) -> Optional[str]:
    """Parse JWT token and get username."""
    try:
        payload = jwt.decode(token, key=settings.SECRET_KEY, algorithms=["HS256"])
        token = schemas.TokenData(**payload)
        return token.username
    except Exception as x:
        raise HTTPException(
            status_code=status_code.HTTP_401_UNAUTHORIZED,
            detail=f"token error: {repr(x):.256}",
        )
    return None


def build_token(user: models.User) -> str:
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
async def get_token(user=Depends(get_user)) -> schemas.TokenResponse:
    """Create auth token for logged-in user."""
    token = build_token(user)
    return {"token": token}


@api.get("/oauth2-login")
async def login_oauth2():
    """Redirect to oAuth2 login form."""
    if settings.AUTH_OAUTH_LOGIN_URL and settings.AUTH_OAUTH_TOKEN_URL:
        return RedirectResponse(settings.AUTH_OAUTH_LOGIN_URL)
    raise HTTPException(status_code=status_code.HTTP_412_PRECONDITION_FAILED)


@api.get("/oauth2-authorize")
def login_oauth2_authorize(code: str, db=Depends(models.db_session)):
    """Authorize oAuth2, get user info -- create user, set cookie."""
    # get access token
    form = {"code": code}
    form.update(settings.AUTH_OAUTH_TOKEN_URL_FORM)
    req_token = request.Request(
        url=settings.AUTH_OAUTH_TOKEN_URL,
        method="POST",
        data=parse.urlencode(form).encode(),
        headers={"Content-Type": "application/x-www-form-urlencoded"},
    )
    rsp_token = json.load(request.urlopen(req_token))
    token = rsp_token.get("access_token")
    token_type = rsp_token.get("token_type")
    # get user info
    req_info = request.Request(
        url=settings.AUTH_OAUTH_USERINFO_URL,
        method="GET",
        headers={"Authorization": f"{token_type} {token}"},
    )
    rsp_info = json.load(request.urlopen(req_info))
    # get or create user, set cookie and redirect to home page
    email = rsp_info.get("email")
    user = get_user(username=email, db=db)
    token = build_token(user)
    response = RedirectResponse(settings.AUTH_OAUTH_FINAL_URL)
    response.set_cookie(key="token", value=token)
    return response

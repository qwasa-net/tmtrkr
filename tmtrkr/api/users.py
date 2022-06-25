"""API for the users (Not fully Implemented Yet)."""

import time
from typing import Optional

import jwt
from authlib.integrations.starlette_client import OAuth
from fastapi import APIRouter, Cookie, Depends, Header, HTTPException, Request
from fastapi import status as status_code
from fastapi.responses import RedirectResponse
from fastapi.security import OAuth2PasswordBearer
from tmtrkr import models, settings
from tmtrkr.api import schemas

__all__ = ["api", "get_user"]


api = APIRouter()

# cached oauth client
_oauth2_client = None


def get_oauth2_client():
    """Create oauth2 client, read provider configuration."""
    if _oauth2_client:
        return _oauth2_client
    oauth = OAuth()
    oauth_client = oauth.register(
        settings.AUTH_OAUTH2_CLIENT_ID,
        client_id=settings.AUTH_OAUTH2_CLIENT_ID,
        client_secret=settings.AUTH_OAUTH2_CLIENT_SECRET,
        server_metadata_url=settings.AUTH_OAUTH2_METADATA_URL,
        client_kwargs={"scope": settings.AUTH_OAUTH2_SCOPE},
    )
    globals()["_oauth2_client"] = oauth_client
    return oauth_client


def get_username(
    auth_token: Optional[str] = Depends(OAuth2PasswordBearer(tokenUrl="", auto_error=False)),
    cookie_token: Optional[str] = Cookie(alias=settings.AUTH_USERS_ALLOW_JWT_COOKIE_BRAND, default=None),
    x_user: Optional[str] = Header(alias=settings.AUTH_USERS_ALLOW_XFORWARDED_HEADER, default=None),
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
    response = RedirectResponse("/")
    response.set_cookie(key=settings.AUTH_USERS_ALLOW_JWT_COOKIE_BRAND, value=None)
    return response


@api.get("/token", response_model=schemas.TokenResponse)
async def get_token(user=Depends(get_user)) -> schemas.TokenResponse:
    """Create auth token for logged-in user."""
    token = build_token(user)
    return {"token": token}


@api.get("/oauth2-login")
async def login_oauth2(req: Request, oauth_client=Depends(get_oauth2_client)):
    """Redirect to oAuth2 login form."""
    return await oauth_client.authorize_redirect(req, settings.AUTH_OAUTH2_AUTHORIZE_URL)


@api.get("/oauth2-authorize")
async def login_oauth2_authorize(
    req: Request,
    oauth_client=Depends(get_oauth2_client),
    db=Depends(models.db_session),
):
    token = await oauth_client.authorize_access_token(req)
    username = token.get("userinfo", {}).get(settings.AUTH_OAUTH_USERINFO_USERNAME)
    user = get_user(username=username, db=db)
    token = build_token(user)
    response = RedirectResponse(settings.AUTH_OAUTH_FINAL_URL)
    response.set_cookie(key=settings.AUTH_USERS_ALLOW_JWT_COOKIE_BRAND, value=token)
    return response


@api.get("/oauth2-logout")
async def logout_oauth2(
    oauth_client=Depends(get_oauth2_client),
):
    """Redirect to oAuth2 login form."""
    if oauth_client.server_metadata and oauth_client.server_metadata.get("end_session_endpoint"):
        return RedirectResponse(url=oauth_client.server_metadata.get("end_session_endpoint"))
    return logout()

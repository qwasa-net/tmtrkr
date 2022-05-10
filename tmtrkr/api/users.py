"""API for the users (Not Implemented Yet)."""

from typing import Optional

import tmtrkr.models as models
import tmtrkr.settings as settings
from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi import status as status_code
from fastapi.security.utils import get_authorization_scheme_param

api = APIRouter()


@api.get("/login")
async def login():
    """Get auth token."""
    raise HTTPException(status_code=status_code.HTTP_418_IM_A_TEAPOT, detail="Not Implemented")


@api.get("/logout")
async def logout():
    """Decativate auth token."""
    raise HTTPException(status_code=status_code.HTTP_418_IM_A_TEAPOT, detail="Not Implemented")


def get_user(req: Request, db=Depends(models.db_session)) -> Optional[models.User]:
    """
    Get user from headers.

    FIXME: Not Implemented Yet!
    This is just a simple stub -- WITHOUT ANY REAL authorization.
    """
    auth = req.headers.get("Authorization")
    if not auth:
        if not settings.AUTH_USERS_ALLOW_UNKNOWN:
            raise HTTPException(status_code=status_code.HTTP_401_UNAUTHORIZED, details="Must be logged-in")
        return None
    scheme, param = get_authorization_scheme_param(auth)
    if scheme.lower() == "basic" and param:
        username, *_ = param.split()
        if settings.AUTH_USERS_AUTO_CREATE:
            user = models.User.get_or_create(db, name=username)
        else:
            user = models.User.first(db, name=username)
        print(param, username, user)
    if not user and not settings.AUTH_USERS_ALLOW_UNKNOWN:
        raise HTTPException(status_code=status_code.HTTP_401_UNAUTHORIZED, details="Must be logged-in")
    return user

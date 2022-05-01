"""API for the users (NotImlementedYet)."""


from fastapi import APIRouter, HTTPException

api = APIRouter()


@api.get("/login")
def login():
    """Get auth token."""
    return HTTPException(status_code=418, detail="Not Implemented")


@api.get("/logout")
def logout():
    """Decativate auth token."""
    return HTTPException(status_code=418, detail="Not Implemented")


def get_user():
    """Return None always -- NotImlementedYet."""
    return None

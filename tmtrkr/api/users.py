"""API for the users (NotImlementedYet)."""


from fastapi import APIRouter, HTTPException

api = APIRouter()


@api.get("/login")
async def login():
    """Get auth token."""
    raise HTTPException(status_code=418, detail="Not Implemented")


@api.get("/logout")
async def logout():
    """Decativate auth token."""
    raise HTTPException(status_code=418, detail="Not Implemented")


def get_user():
    """Return None always -- NotImlementedYet."""
    return None

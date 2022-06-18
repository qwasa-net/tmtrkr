"""Application API root module."""
import fastapi

from tmtrkr.settings import API_BASE_PREFIX, SECRET_KEY

from .records import api as records_api
from .users import api as users_api
from starlette.middleware.sessions import SessionMiddleware

app = fastapi.FastAPI()
app.include_router(records_api, prefix=API_BASE_PREFIX + "/records")
app.include_router(users_api, prefix=API_BASE_PREFIX + "/users")
app.add_middleware(SessionMiddleware, secret_key=SECRET_KEY)

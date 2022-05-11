"""TmTrkr application settings."""
import json
import os

# Database settings
DATABASE_URL = os.environ.get("TMTRKR_DATABASE_URL", "sqlite:///db.sqlite")

if "sqlite" in DATABASE_URL:
    DEFAULT_DATABASE_CONNECT_ARGS = '{"check_same_thread": false}'
else:
    DEFAULT_DATABASE_CONNECT_ARGS = "{}"

DATABASE_CONNECT_ARGS = json.loads(os.environ.get("TMTRKR_DATABASE_CONNECT_ARGS", DEFAULT_DATABASE_CONNECT_ARGS))

# Demo server settings
SERVER_BIND_HOST = os.environ.get("TMTRKR_SERVER_BIND_HOST", "0.0.0.0")
SERVER_BIND_PORT = int(os.environ.get("TMTRKR_SERVER_BIND_PORT", 8000))

# API
API_BASE_PREFIX = "/api"

# API Auth parameters
AUTH_USERS_ALLOW_UNKNOWN = True
AUTH_USERS_ALLOW_BASIC = True
AUTH_USERS_AUTO_CREATE = True

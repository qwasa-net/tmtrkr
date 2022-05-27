"""TmTrkr application settings."""
import json
import os
import random
import string

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
API_PAGE_SIZE_LIMIT = 1000

# API Auth parameters
AUTH_USERS_ALLOW_XFORWARDED = True  # trust `x-forward-user` HTTP header (from nginx or demo UI)
AUTH_USERS_ALLOW_JWT = True  # enable JWT token (in Authorize header or cookie)
AUTH_USERS_ALLOW_JWT_TTL = 60 * 60

AUTH_USERS_ALLOW_UNKNOWN = False  # allow guests
AUTH_USERS_AUTO_CREATE = True  # create new users automatically (when a valid username is passed in the header or token)

# OAuth2 parameters (google flavoured)
AUTH_OAUTH_LOGIN_URL = os.environ.get(
    "TMTRKR_AUTH_OAUTH_LOGIN_URL",
    "https://accounts.google.com/o/oauth2/v2/auth?response_type=code&scope=email&client_id=…&redirect_uri=…",
)
AUTH_OAUTH_TOKEN_URL = os.environ.get(
    "TMTRKR_AUTH_OAUTH_TOKEN_URL",
    "https://oauth2.googleapis.com/token",
)
AUTH_OAUTH_TOKEN_URL_FORM = json.loads(
    os.environ.get(
        "TMTRKR_AUTH_OAUTH_TOKEN_URL_FORM",
        """{"client_id":null,"client_secret":null,"redirect_uri":"…","grant_type":"authorization_code"}""",
    )
)
AUTH_OAUTH_USERINFO_URL = os.environ.get(
    "TMTRKR_AUTH_OAUTH_USERINFO_URL",
    "https://openidconnect.googleapis.com/v1/userinfo",
)
AUTH_OAUTH_FINAL_URL = os.environ.get(
    "TMTRKR_AUTH_OAUTH_FINAL_URL",
    "/?oauth2",
)

#
SECRET_KEY = os.environ.get("TMTRKR_SECRET_KEY", "".join(random.choices(string.ascii_letters, k=64)))

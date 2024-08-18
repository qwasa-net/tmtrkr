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
AUTH_USERS_ALLOW_XFORWARDED = True  # trust `x-forwarded-user` HTTP header (from nginx or demo UI)
AUTH_USERS_ALLOW_XFORWARDED_HEADER = "x-forwarded-user"
AUTH_USERS_ALLOW_JWT = True  # enable JWT token (in Authorize header or cookie)
AUTH_USERS_ALLOW_JWT_COOKIE_BRAND = "tmtrkr-token"
AUTH_USERS_ALLOW_JWT_TTL = 60 * 60

AUTH_USERS_ALLOW_UNKNOWN = False  # allow guests
AUTH_USERS_AUTO_CREATE = True  # create new users automatically (when a valid username is passed in the header or token)

# OAuth2 parameters (google flavoured)
AUTH_OAUTH2_CLIENT_ID = os.environ.get(
    "TMTRKR_AUTH_OAUTH2_CLIENT_ID",
    "tmtrkr",
)
AUTH_OAUTH2_CLIENT_SECRET = os.environ.get(
    "TMTRKR_AUTH_OAUTH2_CLIENT_SECRET",
    "…",
)
AUTH_OAUTH2_METADATA_URL = os.environ.get(
    "TMTRKR_AUTH_OAUTH2_METADATA_URL",
    "https://accounts.google.com/.well-known/openid-configuration",
)
AUTH_OAUTH2_SCOPE = os.environ.get(
    "TMTRKR_AUTH_OAUTH2_SCOPE",
    "openid email profile",
)
AUTH_OAUTH2_AUTHORIZE_URL = os.environ.get(
    "TMTRKR_AUTH_OAUTH2_AUTHORIZE_URL",
    "http://localhost/api/users/oauth2-authorize",
)
AUTH_OAUTH_USERINFO_USERNAME = os.environ.get(
    "TMTRKR_AUTH_OAUTH_USERINFO_USERNAME",
    "email",
)
AUTH_OAUTH_FINAL_URL = os.environ.get(
    "TMTRKR_AUTH_OAUTH_FINAL_URL",
    "/?oauth2",
)

#
SECRET_KEY = os.environ.get("TMTRKR_SECRET_KEY", "".join(random.choices(string.ascii_letters, k=64)))

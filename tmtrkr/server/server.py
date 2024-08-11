"""Demo server."""

import uvicorn
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import RedirectResponse
from fastapi.staticfiles import StaticFiles

import tmtrkr.settings
from tmtrkr.api.api import app
from tmtrkr.server.packagestaticfiles import PackageStaticFiles


def setup_cors(app, origins=None):
    """For demo server allow request from localhost and anywhere."""
    origins = origins or ["http://localhost", "http://localhost:8000", "null", "*"]
    app.add_middleware(
        CORSMiddleware,
        allow_origins=origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )


def mount_static(app, zipapp=False):
    """Serve static files for web front-end."""

    if zipapp:
        app.mount("/www", PackageStaticFiles(directory="www", package="tmtrkr", html=True), name="www")
    else:
        app.mount("/www", StaticFiles(directory="www", html=True), name="www")

    @app.get("/")
    async def index():
        """Simply redirect to index.html page."""
        return RedirectResponse("/www")


def run(zipapp=False):
    """Run server, run."""

    setup_cors(app)
    mount_static(app, zipapp)

    uvicorn.run(
        app,
        access_log=True,
        host=tmtrkr.settings.SERVER_BIND_HOST,
        port=tmtrkr.settings.SERVER_BIND_PORT,
    )


if __name__ == "__main__":
    run()

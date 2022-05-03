"""Demo server."""
import uvicorn
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from tmtrkr.api.api import app
from fastapi.responses import RedirectResponse
import tmtrkr.settings

# For demo server allow request from localhost and anywhere
origins = ["http://localhost", "http://localhost:8000", "null", "*"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Serve static files -- web front-end
app.mount("/client", StaticFiles(directory="client", html=True), name="client")


# Redirect from root to front
@app.get("/")
async def main():
    """Simply redirect to index.html page."""
    return RedirectResponse("/client")


if __name__ == "__main__":
    uvicorn.run(
        "tmtrkr.api.api:app",
        reload=True,
        access_log=True,
        host=tmtrkr.settings.SERVER_BIND_HOST,
        port=tmtrkr.settings.SERVER_BIND_PORT,
    )

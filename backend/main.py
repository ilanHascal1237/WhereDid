from fastapi import FastAPI, Request
from fastapi.exceptions import HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from dotenv import load_dotenv
import logging
import os
import threading
from app.db import MongoDB
from app.routes import game, players
from app.services import espn, DataNotReadyError

load_dotenv()

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Connect to MongoDB on startup
MongoDB.connect_db()


def _sync_in_background():
    try:
        espn.sync_players()
    except Exception:
        logging.exception("ESPN player sync failed")


# Pull fresh rosters from ESPN when the DB is empty or stale. Runs in a
# thread so the API is available immediately. Set AUTO_SYNC=false to skip.
if os.getenv("AUTO_SYNC", "true").lower() != "false" and espn.needs_sync():
    threading.Thread(target=_sync_in_background, daemon=True).start()

app = FastAPI(
    title="WhereDid API",
    description="NBA & NFL Player Guessing Game API",
    version="0.1.0"
)

# Enable CORS
origins = [
    "http://localhost",
    "http://localhost:5173",
    "http://localhost:8000",
    os.getenv("FRONTEND_URL", "http://localhost:5173"),
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.exception_handler(DataNotReadyError)
async def data_not_ready_handler(request: Request, exc: DataNotReadyError):
    """Data (players/colleges) hasn't finished syncing yet - this is a
    transient state, not a server bug, so it gets a 503 rather than a 500."""
    return JSONResponse(
        status_code=503,
        content={"detail": "Data is still syncing. Please try again shortly."},
    )


@app.exception_handler(Exception)
async def unhandled_exception_handler(request: Request, exc: Exception):
    """Catch-all for anything a route didn't handle explicitly. Logs the real
    error server-side and returns a generic message so raw exception text
    (which may include Mongo/driver internals) never reaches the client.

    FastAPI's HTTPException is handled by its own default handler before
    this one ever runs, so explicit 404s etc. raised in routes are untouched.
    """
    logger.exception("Unhandled exception while processing %s %s", request.method, request.url.path)
    return JSONResponse(
        status_code=500,
        content={"detail": "Internal server error"},
    )


@app.get("/")
def read_root():
    return {
        "message": "Welcome to WhereDid API",
        "version": "0.1.0"
    }

@app.get("/health")
def health_check():
    return {"status": "healthy"}

# Include routes
app.include_router(game.router)
app.include_router(players.router)

@app.on_event("shutdown")
def shutdown():
    """Close MongoDB connection on shutdown"""
    MongoDB.close_db()

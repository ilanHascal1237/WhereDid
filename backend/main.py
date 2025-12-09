from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
import os
from app.db import MongoDB
from app.routes import game, players

load_dotenv()

# Connect to MongoDB on startup
MongoDB.connect_db()

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

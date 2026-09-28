"""
FastAPI application — Smart Developer Onboarding Assistant.

Routes:
  GET  /             → service status and available API endpoints
  GET  /health       → health check
  POST /analyze-all  → repo summary, architecture, setup guide, starter tasks (all 4 in parallel)
  POST /download     → assembles full report into a .md file download
"""

import os
import pathlib

from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.routing import APIRoute

# Load backend/.env so GROQ_MODEL and GROQ_API_KEY* are available regardless
# of the working directory the server is started from.
load_dotenv(pathlib.Path(__file__).parent / ".env")

from backend.routers import analyze_all, download

app = FastAPI(title="Onboard.ai", version="0.1.0")

_ALLOWED_ORIGINS = [
    "http://localhost:5173",
    os.getenv("FRONTEND_URL", ""),
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=[o for o in _ALLOWED_ORIGINS if o],
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(analyze_all.router)
app.include_router(download.router)


@app.get("/health")
async def health() -> dict[str, str]:
    return {"status": "ok"}


@app.get("/")
async def root() -> dict[str, str | list[str]]:
    endpoints = list(
        dict.fromkeys(
            route.path
            for route in app.routes
            if isinstance(route, APIRoute) and route.path != "/"
        )
    )
    return {"status": "ok", "endpoints": endpoints}

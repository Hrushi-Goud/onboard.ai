"""
FastAPI application — Smart Developer Onboarding Assistant.

Routes:
  POST /analyze-all  → repo summary, architecture, setup guide, starter tasks (all 4 in parallel)
  POST /download     → assembles full report into a .md file download
"""

import pathlib

from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# Load backend/.env so GROQ_MODEL and GROQ_API_KEY* are available regardless
# of the working directory the server is started from.
load_dotenv(pathlib.Path(__file__).parent / ".env")

from backend.routers import analyze_all, download

app = FastAPI(title="Smart Developer Onboarding Assistant", version="0.1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(analyze_all.router)
app.include_router(download.router)

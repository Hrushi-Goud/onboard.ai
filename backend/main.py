"""
FastAPI application — Smart Developer Onboarding Assistant.

Routes:
  POST /analyze               → repo summary + file structure
  POST /explain-architecture  → architecture explanation + Mermaid diagram
  POST /setup-guide           → local setup instructions
  POST /starter-tasks         → starter tasks + optimization suggestions
  GET  /download              → assembles all 6 sections into a .md file download
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(title="Smart Developer Onboarding Assistant", version="0.1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Routes are registered in the routers package (imported below once it exists).
# For now this file boots cleanly and the server can be started immediately.

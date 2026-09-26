"""POST /analyze-all — fetch context once, run all 4 Groq tools in parallel, return full report."""

from __future__ import annotations

import httpx
from fastapi import APIRouter, HTTPException

from backend.groq_client import GroqClient, GroqConfigurationError, GroqResponseError, OnboardingReport
from backend.schemas import RepoRequest
from backend.services.repo_context import fetch_repo_context, parse_github_url

router = APIRouter()
_groq = GroqClient()


@router.post("/analyze-all", response_model=OnboardingReport)
async def analyze_all(body: RepoRequest) -> OnboardingReport:
    """Fetch repo context once, then run all 4 Groq tools concurrently via asyncio.gather.

    Returns the complete OnboardingReport in one shot — the frontend can pass
    this directly to POST /download to get the .md file.
    """
    try:
        owner, repo = parse_github_url(body.repo_url)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc

    try:
        context = await fetch_repo_context(owner, repo)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except (httpx.HTTPStatusError, httpx.RequestError) as exc:
        raise HTTPException(status_code=503, detail=f"GitHub fetch failed: {exc}") from exc

    try:
        return await _groq.analyze_all(context)
    except (GroqResponseError, GroqConfigurationError) as exc:
        raise HTTPException(status_code=502, detail=str(exc)) from exc

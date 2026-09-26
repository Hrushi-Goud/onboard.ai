"""Pydantic models for the FastAPI API layer.

Response types are imported directly from groq_client to avoid duplication.
"""

from __future__ import annotations

from pydantic import BaseModel, Field

from backend.groq_client import (  # noqa: F401
    ArchitectureExplanation,
    OnboardingReport,
    RepositoryAnalysis,
    SetupGuide,
    StarterTasksAndOptimizations,
)


class RepoRequest(BaseModel):
    """Request body for POST /analyze-all."""

    repo_url: str = Field(min_length=1, description="Public GitHub repository URL.")


class DownloadRequest(BaseModel):
    """Request body for POST /download.

    The frontend calls POST /analyze-all, gets back an OnboardingReport, then
    posts that same JSON here with repo_url added to receive the .md download.
    """

    repo_url: str = Field(min_length=1)
    analysis: RepositoryAnalysis
    architecture: ArchitectureExplanation
    setup_guide: SetupGuide
    starter_tasks_and_optimizations: StarterTasksAndOptimizations

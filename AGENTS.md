# AGENTS.md

This file provides guidance to agents when working with code in this repository.

## Project Overview

Smart Developer Onboarding Assistant — project developed in the context of the IBM Bob 2.0 Hackathon.
Stack: **FastAPI** (backend) + **React** (frontend) + **Groq API** (AI analysis layer).

## Planned Architecture

- `backend/` — FastAPI app; 4 core endpoints: analyze, explain-architecture, setup-guide, starter-tasks
- `frontend/` — React app; single page: repo URL input → tabbed report (Architecture / Setup / Starter Tasks)
- FastAPI retrieves and selects repository files, then calls Groq to analyze the supplied context; Groq does not fetch repositories from URLs
- Once repository context is ready, launch the four independent Groq analyses concurrently with `GroqClient.analyze_all`; keep single-capability methods available for incremental endpoint use

## Key Project-Specific Decisions (from plan-brief.md)

- **PDF export was intentionally dropped** — export is Markdown-only (simpler, fewer moving parts)
- **Architecture diagrams use Mermaid syntax** — ask Groq for Mermaid in the same request as the architecture explanation
- **React renders Mermaid in-browser** using the `mermaid` JS library
- **FastAPI assembles all 6 sections** into a single `.md` string for the download endpoint
- The 6 report sections are: repo analysis/summary, architecture + diagram, file structure, setup guidance, starter tasks, optimization suggestions

## Commands

> The backend has an initial FastAPI scaffold; the frontend and remaining API implementation are still planned.

### Backend (FastAPI)
```bash
# From backend/
pip install -r requirements.txt
uvicorn main:app --reload
pytest                        # run all tests
pytest tests/test_analyze.py  # run single test file
```

### Frontend (React)
```bash
# From frontend/
npm install
npm run dev      # Vite dev server (assumed)
npm test         # or: npx vitest run <file> for single test
npm run build
npm run lint
```

## Code Style Guidelines

> To be locked in once scaffolding starts. Defaults to follow:

- **Python**: Black formatting, type hints on all function signatures, `async def` for all FastAPI route handlers
- **TypeScript/JS**: Prefer TypeScript; no `any` types; functional React components only
- **Imports**: absolute imports preferred; no barrel files unless intentional
- **Naming**: snake_case in Python, camelCase in JS/TS, PascalCase for React components
- **Error handling**: FastAPI routes should use `HTTPException` with explicit status codes; React should surface errors in UI, never silently swallow them

## Critical Context

- Demo target repo is `finance-tracker-api` — test all 4 core capabilities against it before submitting
- Confirm the Groq model, API limits, response format, and repository context strategy before finalizing the backend integration
- watsonx Orchestrate and watsonx.ai features are **optional stretch goals** — do not block core work on them

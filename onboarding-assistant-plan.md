# Plan: Smart Developer Onboarding Assistant
**Hackathon context: IBM Bob 2.0 Hackathon — lablab.ai (Sept 25–27, 2026)**
**AI provider: Groq**

---

## Top-Level Overview

Build a web application that takes a GitHub repository URL and generates a structured, 6-section developer onboarding report using Groq to analyze repository context gathered by the backend.

- **Backend:** FastAPI — 4 analysis endpoints + 1 download endpoint
- **Frontend:** React — single-page input form + tabbed report display + Markdown download
- **AI Layer:** Groq API — analyzes bounded repository context supplied by the backend; the backend, not Groq, is responsible for retrieving repository files
- **Export:** Markdown-only (PDF dropped); Mermaid diagrams rendered in-browser via `mermaid` JS

The work is divided across **5 roles**: Groq Integration, Backend Core, Frontend UI, Diagram + Export, and QA + Demo.

---

## Person 1 — Groq Integration Engineer

**Intent:** Own the Groq API integration and prompt/output contract. Coordinate with the backend owner to ensure repository context is retrieved and selected before it is sent to the model.

**Expected Outcomes:**
- Groq can be called asynchronously from Python using the official SDK
- Prompts are validated to produce all 6 report sections reliably
- A thin Python client module (`groq_client.py`) wraps Groq and is usable by Person 2

**Todo List:**
1. Confirm Groq account access, select a supported model, and check API limits and supported response formats
2. Validate prompts against representative files from the `finance-tracker-api` test repo for each of the 4 required capabilities
3. Design and validate prompts for each section: repo summary, architecture + Mermaid diagram (single call), file structure, setup guidance, starter tasks, optimization suggestions
4. Confirm that architecture + Mermaid diagram can reliably come from one Groq request
5. Write `backend/groq_client.py` — a thin async wrapper with one callable per analysis capability
6. Document prompt templates, configured model behavior, and expected response shapes
7. Define how the backend passes repository context to the client without exceeding practical context limits

**Relevant Context:**
- `plan-brief.md` — confirm the Groq model/API limits and backend repository retrieval strategy before finalizing the integration
- `backend/.env.example` — currently documents separate Groq API keys for the four analysis methods; keep secrets server-side
- The 6 sections: repo summary, architecture + diagram, file structure, setup guidance, starter tasks, optimization suggestions

**Status:** [ ] pending

---

## Person 2 — Backend Engineer (FastAPI)

**Intent:** Build the FastAPI application with all 5 endpoints, including backend repository retrieval and context selection. Depends on Person 1's `groq_client.py` module being available (or mock-ready) to wire up the analysis routes.

**Expected Outcomes:**
- FastAPI app runs via `uvicorn main:app --reload` from `backend/`
- 4 analysis endpoints each pass selected repository context to the appropriate Groq client function and return structured JSON
- The Groq client exposes `analyze_all()` to run the four independent capability calls concurrently when a complete report is requested
- 1 download endpoint assembles all 6 sections into a single `.md` string and serves it as a file
- `requirements.txt` is complete and accurate
- All routes use `async def` and raise `HTTPException` with explicit status codes on error

**Todo List:**
1. Review the existing `backend/main.py` and `requirements.txt`; complete the API, router, service, and test structure
2. Implement a backend-only service to validate a GitHub URL, retrieve repository files, and select bounded context for analysis
3. Implement `POST /analyze` — supplies repo context to Groq for the repo summary section
4. Implement `POST /explain-architecture` — supplies repo context for architecture + Mermaid diagram (single request)
5. Implement `POST /setup-guide` — supplies repo context for setup guidance
6. Implement `POST /starter-tasks` — supplies repo context for starter tasks + optimization suggestions
7. Implement `GET /download` — assembles all 6 sections into one `.md` string and serves it as a file download
8. Add CORS middleware to allow the React frontend to call the API
9. Write `tests/test_analyze.py` covering happy path and error cases for each endpoint, including repository retrieval and Groq failures

**Relevant Context:**
- `AGENTS.md` — backend run command: `uvicorn main:app --reload`; test command: `pytest`
- `AGENTS.md` — "async def for all FastAPI route handlers", "HTTPException with explicit status codes"
- `backend/requirements.txt` already includes the Groq SDK; `backend/.env.example` documents Groq key configuration
- The 6 sections must all be assembled by the download endpoint into a single `.md` string

**Status:** [ ] pending

---

## Person 3 — Frontend Engineer (React)

**Intent:** Build the React single-page application — repo URL input form, tabbed report display, and download button. No auth, no routing, no database. Simple and demo-ready.

**Expected Outcomes:**
- App runs via `npm run dev` from `frontend/`
- User pastes a repo URL, clicks "Analyze", sees a loading state, then a tabbed report
- Tabs: Architecture, Setup, Starter Tasks (minimum); all 6 sections accessible in the UI
- Download button triggers the backend `/download` endpoint and saves a `.md` file
- All components are functional React, written in TypeScript, no `any` types
- Errors from the backend are surfaced in the UI, never silently swallowed

**Todo List:**
1. Scaffold `frontend/` with Vite + React + TypeScript
2. Build `RepoInputForm` component — text input for repo URL + submit button + loading state
3. Build `ReportTabs` component — tab navigation across the 6 report sections
4. Build individual section display components: `ArchitectureTab`, `SetupTab`, `StarterTasksTab`, `SummaryTab`, `FileStructureTab`, `OptimizationsTab`
5. Wire up API calls to all 4 backend endpoints concurrently once repository context is ready (or use the coordinated full-report flow)
6. Add `DownloadButton` component that calls `/download` and triggers `.md` file save in-browser
7. Add error boundary / error display for failed API calls
8. Add `npm run lint` passing with no warnings

**Relevant Context:**
- `AGENTS.md` — "Prefer TypeScript; no `any` types; functional React components only"
- `AGENTS.md` — "React should surface errors in UI, never silently swallow them"
- `plan-brief.md` — "simple page where you paste a repo link and get a readable report"
- Person 4 owns Mermaid rendering — Person 3 only needs to render a placeholder `<div>` for the diagram slot

**Status:** [ ] pending

---

## Person 4 — Diagram + Export Engineer

**Intent:** Own two specific technical pieces: (1) rendering Mermaid diagrams in-browser inside the React app, and (2) the Markdown assembly + download flow on the backend. Both are isolated enough to be owned by one person.

**Expected Outcomes:**
- `mermaid` JS library is integrated into the React app; raw Mermaid syntax from Groq renders as a live diagram
- The diagram auto-re-renders when the content changes (new repo analyzed)
- The backend `/download` endpoint produces a valid `.md` file containing all 6 sections including the raw Mermaid code block
- The `.md` file renders correctly when opened in GitHub, GitLab, or any standard Markdown viewer

**Todo List:**
1. Install and configure `mermaid` JS in the React frontend
2. Build `MermaidDiagram` component — takes raw Mermaid string as a prop, renders the diagram in-browser
3. Integrate `MermaidDiagram` into the `ArchitectureTab` component (coordinate with Person 3)
4. Handle Mermaid render errors gracefully — show raw code block as fallback if diagram fails to parse
5. On the backend: implement the Markdown assembly template in the `/download` endpoint — all 6 sections in order, with the Mermaid block wrapped in a fenced code block (` ```mermaid ... ``` `)
6. Validate the exported `.md` renders correctly on GitHub by checking against a real file
7. Test that the in-browser diagram and the exported Mermaid block both come from the same architecture response (no duplicate request)

**Relevant Context:**
- `plan-brief.md` — "React frontend renders the Mermaid live on-screen using the mermaid JS library (lightweight, in-browser)"
- `plan-brief.md` — "FastAPI assembles all 6 sections (including the raw Mermaid code block) into one .md string, served as a file download"
- `plan-brief.md` — ask Groq to output the architecture explanation and Mermaid syntax in the same request
- The Mermaid code block is part of the architecture response from Groq — Person 1 must confirm the exact response shape

**Status:** [ ] pending

---

## Person 5 — QA + Demo Engineer

**Intent:** Own end-to-end testing, the demo script, and the impact framing. This person ensures the full pipeline works on the `finance-tracker-api` demo repo and that the submission tells a clear, compelling story to judges.

**Expected Outcomes:**
- All 4 required capabilities verified working end-to-end on `finance-tracker-api`
- A recorded or live demo showing: paste URL → generate report → view architecture diagram → download `.md`
- A clear "before/after" impact statement: estimated time saved per new dev onboarded
- `pytest` passes for all backend tests; `npm test` passes for frontend tests
- Submission materials (README, demo video or link, lablab.ai submission form) are complete

**Todo List:**
1. Set up a local environment running both backend and frontend simultaneously
2. Run end-to-end test on `finance-tracker-api` — verify all 6 report sections are generated correctly
3. Verify the Mermaid diagram renders in-browser for `finance-tracker-api`
4. Verify the `.md` download contains all 6 sections and the Mermaid block renders on GitHub
5. Write and run `pytest` for backend; confirm all tests pass
6. Write and run frontend tests; confirm `npm test` passes
7. Draft the demo script: open with the pain point → live analysis of `finance-tracker-api` → show all tabs → download report → end with impact number
8. Write the impact framing: "onboarding this repo used to take ~2 days → now takes 20 minutes" with a concrete before/after
9. Write `README.md` covering: what the app does, how to run it (backend + frontend), how repository context is prepared, and how Groq is used
10. Complete the lablab.ai submission form with demo link, repo link, and team info

**Relevant Context:**
- `AGENTS.md` — "Demo target repo is `finance-tracker-api` — test all 4 core capabilities against it before submitting"
- `plan-brief.md` — "Show the tool generating a guide live (or via recording) on the finance-tracker-api repo, hitting all 4 required capabilities"
- `plan-brief.md` — "End with the impact number: estimated time saved per new dev onboarded"
- `plan-brief.md` — "Add a simple before/after framing: onboarding this repo used to take ~2 days of reading → now takes 20 minutes"

**Status:** [ ] pending

---

## Dependency Order

```
Person 1 (Groq Integration)
    └── unblocks → Person 2 (Backend)
                        └── unblocks → Person 3 + 4 (Frontend + Diagram/Export) in parallel
                                            └── unblocks → Person 5 (QA + Demo)
```

Person 3 and Person 4 can start scaffolding in parallel with Person 2, but need Person 2's endpoints and Person 1's confirmed Groq response shapes before wiring up real data.

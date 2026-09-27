# Plan: Smart Developer Onboarding Assistant
**Hackathon context: IBM Bob 2.0 Hackathon — lablab.ai (Sept 25–27, 2026)**
**AI provider: Groq**

---

## Top-Level Overview

Build a web application that takes a GitHub repository URL and generates a structured, 6-section developer onboarding report using Groq to analyze repository context gathered by the backend.

- **Backend:** FastAPI — 2 endpoints: `POST /analyze-all` (runs all 4 Groq capabilities concurrently) + `POST /download` (assembles full `.md` report)
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
- TPM throttling is enforced per API key (8,000 TPM limit per key)
- Mermaid diagram output is sanitised to prevent parse errors in the frontend

**Todo List:**
1. Confirm Groq account access, select a supported model, and check API limits and supported response formats
2. Validate prompts against representative files from the `finance-tracker-api` test repo for each of the 4 required capabilities
3. Design and validate prompts for each section: repo summary, architecture + Mermaid diagram (single call), file structure, setup guidance, starter tasks, optimization suggestions
4. Confirm that architecture + Mermaid diagram can reliably come from one Groq request
5. Write `backend/groq_client.py` — a thin async wrapper with one callable per analysis capability plus `analyze_all()` that runs all four concurrently via `asyncio.gather`
6. Add per-key TPM throttle (`_TpmThrottle`) to prevent 429 rate-limit errors when all 4 calls fire in parallel
7. Add `_sanitise_mermaid()` post-processor to strip parentheses from Mermaid node/edge labels (Mermaid parse error prevention)
8. Document prompt templates, configured model behavior, and expected response shapes

**Relevant Context:**
- `backend/groq_client.py` — complete; model `openai/gpt-oss-120b`, 4 separate API keys (GROQ_API_KEY1–4), each with 8,000 TPM
- `backend/.env.example` — documents separate Groq API keys for the four analysis methods; secrets stay server-side
- The 6 sections: repo summary, architecture + diagram, file structure, setup guidance, starter tasks, optimization suggestions
- `_TpmThrottle` class — sliding 60-second window per key; sleeps until estimated tokens fit within budget
- `_sanitise_mermaid()` — strips `()` from inside `[node labels]` and `|edge labels|` via regex

**Status:** [x] done

---

## Person 2 — Backend Engineer (FastAPI)

**Intent:** Build the FastAPI application. Design evolved from 4 individual endpoints to a single `POST /analyze-all` endpoint that calls all 4 Groq capabilities concurrently and returns the complete `OnboardingReport` in one shot. The frontend calls this once and passes the result to `POST /download`.

**Expected Outcomes:**
- FastAPI app runs via `uvicorn backend.main:app --reload` from project root
- `POST /analyze-all` fetches GitHub context once, runs all 4 Groq tools concurrently, returns full `OnboardingReport` JSON
- `POST /download` accepts the `OnboardingReport` JSON + `repo_url`, returns a `.md` file download
- CORS allows `http://localhost:5173` (Vite dev) and `*`
- All routes use `async def` and raise `HTTPException` with explicit status codes on error
- `pytest` passes for all 22 backend unit/endpoint tests

**Todo List:**
1. Review and complete `backend/main.py` and `requirements.txt`
2. Implement `backend/services/repo_context.py` — `parse_github_url()` + `fetch_repo_context()` (async, httpx, 20k char cap, excludes secrets/binaries)
3. Implement `backend/schemas.py` — `RepoRequest`, `DownloadRequest`; re-export Groq response types
4. Implement `POST /analyze-all` in `backend/routers/analyze_all.py` — parse URL → fetch context → `_groq.analyze_all(context)` → return `OnboardingReport`
5. Implement `POST /download` in `backend/routers/download.py` — assemble 6-section `.md` from request body, return as attachment
6. Wire both routers in `backend/main.py`
7. Write `backend/tests/test_analyze.py` — 22 tests covering happy paths, all error codes (400/502/503), `/download` standalone, and `parse_github_url` unit tests

**Relevant Context:**
- `backend/routers/analyze_all.py` — single `POST /analyze-all` route; calls `_groq.analyze_all(context)`
- `backend/routers/download.py` — pure formatter; no GitHub or Groq calls; takes `DownloadRequest`, returns `.md`
- `backend/services/repo_context.py` — fetches GitHub recursive file tree, filters, caps at 20,000 chars
- `backend/schemas.py` — `RepoRequest` (repo_url), `DownloadRequest` (repo_url + 4 report sections)
- `backend/tests/test_analyze.py` — 22 passing tests; mocks `fetch_repo_context` and `_groq.analyze_all`
- `backend/tests/test_live_integration.py` — live end-to-end test with real GitHub + real Groq; auto-retries on 429; saves `live_report.md`
- Error mapping: invalid URL → 400; GitHub fetch failure → 503; `GroqResponseError`/`GroqConfigurationError` → 502

**Status:** [x] done

---

## Person 3 — Frontend Engineer (React)

**Intent:** Build the React single-page application — repo URL input form, tabbed report display, and download button. Calls `POST /analyze-all` once to get the full report, then renders each section in its own tab. No auth, no routing, no database.

**Expected Outcomes:**
- App runs via `npm run dev` from `frontend/`
- User pastes a repo URL, clicks "Analyze", sees a loading state, then a tabbed report
- Tabs display all 6 sections: Summary, Architecture, File Structure, Setup Guide, Starter Tasks, Optimization Suggestions
- Download button calls `POST /download` with the cached report JSON and saves a `.md` file
- All components are functional React, written in JavaScript (`.jsx`), no TypeScript
- Errors from the backend are surfaced in the UI, never silently swallowed

**Todo List:**
1. Scaffold `frontend/` with Vite + React + JavaScript (no TypeScript)
2. Build `RepoInputForm` component — text input for repo URL + submit button + loading state
3. Build `ReportTabs` component — tab navigation across the 6 report sections
4. Build individual section display components: `SummaryTab`, `ArchitectureTab`, `FileStructureTab`, `SetupTab`, `StarterTasksTab`, `OptimizationsTab`
5. Wire `POST /analyze-all` call on form submit — store full `OnboardingReport` in state; pass each section to its tab component
6. Add `DownloadButton` component that calls `POST /download` with the cached report + `repo_url` and triggers `.md` file save in-browser
7. Add error display for failed API calls
8. Add `npm run lint` passing with no warnings

**Relevant Context:**
- Backend `POST /analyze-all` returns the full `OnboardingReport` in one shot — one API call populates all tabs
- Backend `POST /download` accepts `{ repo_url, analysis, architecture, setup_guide, starter_tasks_and_optimizations }` — pass the spread of the `/analyze-all` response plus `repo_url`
- Person 4 owns Mermaid rendering — Person 3 renders a placeholder `<div id="mermaid-container">` in `ArchitectureTab` for Person 4 to hook into
- `plan-brief.md` — "simple page where you paste a repo link and get a readable report"
- Stack: Vite + React + JavaScript (`.jsx` files, no TypeScript, no `tsconfig`)

**Status:** [x] done

---

## Person 4 — Diagram + Markdown Rendering Engineer

**Intent:** Own two specific pieces: (1) rendering the Mermaid diagram in-browser inside the React app's `ArchitectureTab`, and (2) rendering all Markdown content (bold, lists, headings, inline code) properly across every tab. Right now the backend returns Markdown-formatted strings (e.g. `**bold**`, numbered lists) but all tabs render them as raw plain text via `<p>` tags. Person 4 fixes both issues.

**Expected Outcomes:**
- `react-markdown` is installed and all tabs that show Groq-generated text render proper HTML (bold, lists, headings, code blocks)
- `mermaid` JS library is integrated into the React app; raw Mermaid syntax from Groq renders as a live diagram in `ArchitectureTab`
- The diagram re-renders correctly when a new repo is analyzed
- Mermaid render errors fall back to a raw `<pre><code>` fenced block (the backend already sanitises parentheses, but render errors can still occur)
- The backend `POST /download` produces a valid `.md` file with all 6 sections and a fenced Mermaid code block — validated against GitHub rendering

**Todo List:**
1. `cd frontend && npm install react-markdown mermaid` — add both packages
2. Build `frontend/src/components/MarkdownRenderer.jsx` — a thin wrapper around `<ReactMarkdown>` that accepts a `children` string prop; use this everywhere Groq text is rendered
3. Build `frontend/src/components/MermaidDiagram.jsx` — accepts a `chart` string prop; on mount/update calls `mermaid.render()` and injects the SVG; on error shows a `<pre><code>` fallback
4. Update `SummaryTab.jsx` — replace `<p>{analysis.summary}</p>` with `<MarkdownRenderer>{analysis.summary}</MarkdownRenderer>`
5. Update `ArchitectureTab.jsx` — replace `<p style={{ whiteSpace:'pre-wrap' }}>{architecture.explanation}</p>` with `<MarkdownRenderer>{architecture.explanation}</MarkdownRenderer>`; replace the placeholder `<div id="mermaid-container">` block with `<MermaidDiagram chart={architecture.mermaid} />`
6. Update `SetupTab.jsx` — the `verification` field is Groq prose; wrap it: `<MarkdownRenderer>{setupGuide.verification}</MarkdownRenderer>`; also wrap individual `step` items that contain inline code (backticks) with `<MarkdownRenderer>`
7. Handle Mermaid render errors gracefully — show raw fenced code block as fallback
8. Validate `POST /download` output — open `backend/tests/live_report.md` on GitHub, confirm all 6 sections and Mermaid block render correctly
9. Confirm the in-browser diagram and the exported Mermaid block both come from the same `/analyze-all` response (no duplicate Groq request)
10. Run `npm run lint` — confirm 0 warnings and 0 errors before marking done

**Relevant Context — what Person 3 already built (do NOT re-implement):**
- `frontend/src/App.jsx` — root component; handles API call, state, error display; renders all 6 sections inline (no `ReportTabs` used — the tab component exists but App renders sections directly)
- `frontend/src/components/tabs/SummaryTab.jsx` — renders `analysis.summary` as `<p>{analysis.summary}</p>` → **needs MarkdownRenderer**
- `frontend/src/components/tabs/ArchitectureTab.jsx` — renders `architecture.explanation` with `whiteSpace:'pre-wrap'`; has `<div id="mermaid-container" data-mermaid={architecture.mermaid}>` placeholder → **needs both MarkdownRenderer + MermaidDiagram**
- `frontend/src/components/tabs/FileStructureTab.jsx` — renders `{ path, purpose }` pairs; purpose is plain text, no Markdown needed
- `frontend/src/components/tabs/SetupTab.jsx` — renders prerequisites/steps as lists, env vars, verification text → **verification field needs MarkdownRenderer**
- `frontend/src/components/tabs/StarterTasksTab.jsx` — task title + description + file chips; description is plain prose, no Markdown needed
- `frontend/src/components/tabs/OptimizationsTab.jsx` — suggestion + rationale + file chips; rationale is plain prose, no Markdown needed
- `frontend/src/components/DownloadButton.jsx` — calls `POST /download`, triggers `.md` blob save; fully working, do not touch
- `frontend/src/components/RepoInputForm.jsx` — URL input + submit button; fully working, do not touch
- `backend/routers/download.py` — already implemented; wraps `architecture.mermaid` in ` ```mermaid ``` ` fenced block
- `backend/groq_client.py` — `_sanitise_mermaid()` strips `()` from labels before the response is returned; diagram should parse cleanly
- `backend/tests/live_report.md` — the last real generated report; use this to verify the Mermaid block renders on GitHub
- `backend/backend_analyze_all_repsonse.json` — full sample API response; use for local dev/testing without hitting the backend

**Key implementation note for MermaidDiagram:**
```jsx
// frontend/src/components/MermaidDiagram.jsx
import { useEffect, useRef, useState } from 'react';
import mermaid from 'mermaid';

mermaid.initialize({ startOnLoad: false, theme: 'default' });

export default function MermaidDiagram({ chart }) {
  const ref = useRef(null);
  const [error, setError] = useState(false);

  useEffect(() => {
    if (!chart || !ref.current) return;
    setError(false);
    const id = 'mermaid-' + Math.random().toString(36).slice(2);
    mermaid.render(id, chart)
      .then(({ svg }) => { ref.current.innerHTML = svg; })
      .catch(() => setError(true));
  }, [chart]);

  if (error) return <pre><code>{chart}</code></pre>;
  return <div ref={ref} />;
}
```

**Status:** [ ] pending

---

## Person 5 — QA + Demo Engineer

**Intent:** Own end-to-end testing, the demo script, and the impact framing. Ensures the full pipeline works on the `finance-tracker-api` demo repo and that the submission tells a clear, compelling story to judges.

**Expected Outcomes:**
- All 4 required capabilities verified working end-to-end on `finance-tracker-api` via `POST /analyze-all`
- A recorded or live demo showing: paste URL → generate report → view architecture diagram → download `.md`
- A clear "before/after" impact statement: estimated time saved per new dev onboarded
- `pytest` passes for all backend tests; `npm test` passes for frontend tests
- Submission materials (README, demo video or link, lablab.ai submission form) are complete

**Todo List:**
1. Set up a local environment running both backend (`uvicorn backend.main:app --reload`) and frontend (`npm run dev`) simultaneously
2. Run end-to-end test on `finance-tracker-api` — verify all 6 report sections are generated correctly via `POST /analyze-all`
3. Verify the Mermaid diagram renders in-browser for `finance-tracker-api`
4. Verify the `.md` download (via `POST /download`) contains all 6 sections and the Mermaid block renders on GitHub
5. Run `pytest` for backend; confirm all tests pass
6. Run frontend tests; confirm `npm test` passes
7. Draft the demo script: open with the pain point → live analysis of `finance-tracker-api` → show all tabs → download report → end with impact number
8. Write the impact framing: "onboarding this repo used to take ~2 days → now takes 20 minutes" with a concrete before/after
9. Write `README.md` covering: what the app does, how to run it (backend + frontend), how repository context is prepared, and how Groq is used
10. Complete the lablab.ai submission form with demo link, repo link, and team info

**Relevant Context:**
- Backend run command: `uvicorn backend.main:app --reload` from project root
- `backend/tests/test_live_integration.py` — live end-to-end test; run this first to confirm the full backend pipeline works
- `backend/tests/live_report.md` — most recent real report from `finance-tracker-api`; use as reference for what the output looks like
- `plan-brief.md` — "Show the tool generating a guide live on the finance-tracker-api repo, hitting all 4 required capabilities"

**Status:** [ ] pending

---

## Dependency Order

```
Person 1 (Groq Integration) — DONE
    └── unblocks → Person 2 (Backend) — DONE
                        └── unblocks → Person 3 + 4 (Frontend + Diagram/Export) in parallel
                                            └── unblocks → Person 5 (QA + Demo)
```

Person 3 and Person 4 can start scaffolding in parallel; both need Person 2's endpoints before wiring up real data.

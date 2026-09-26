# Project Brief: Smart Developer Onboarding Assistant

**Hackathon context: IBM Bob 2.0 Hackathon (lablab.ai) — Sept 25–27, 2026**
**Implementation AI provider: Groq**

## Context

- 48-hour hackathon challenge focused on IBM's agentic AI coding assistant, "Bob 2.0"
- $10,000 prize pool, solo or team, submission via lablab.ai platform
- Judging focuses on demonstrable impact: time saved, errors reduced, productivity gained — not just a working demo
- Successful submission earns a lablab.ai Certificate of Completion (based on prior IBM Bob Hackathon precedent)

## Challenge Context

**Smart Developer Onboarding Assistant**

The challenge asks teams to help new developers understand and contribute to an unfamiliar codebase faster, with repository analysis, architecture explanations, setup guidance, and starter tasks. The original challenge describes IBM Bob as its AI tool. This project has since switched its implementation to Groq; that provider change may affect alignment with the challenge's stated requirements and should be confirmed against the submission rules.

### Required capabilities (core scope)

1. **Repository analysis** — the backend gathers relevant repository files and Groq analyzes the supplied context
2. **Architecture explanation** — plain-English breakdown of how the system is organized and how key flows work
3. **Setup guidance** — auto-generated instructions for getting the project running locally
4. **Starter task suggestions** — Groq suggests specific, low-risk first tasks a new dev could tackle

### Optional stretch features (only after core works)

- **watsonx Orchestrate** — automate onboarding steps (e.g. auto-generate a checklist, sequence the setup steps as a guided flow)
- **watsonx.ai** — add a conversational layer so new devs can *ask questions* about the repo instead of only reading a static report

### Tech stack

- **Backend:** FastAPI — handles repo input, gathers bounded repository context, calls Groq, and returns structured results
- **Frontend:** React — simple page where you paste a repo link and get a readable report
- **AI layer:** Groq API, using a configured supported model to analyze repository context provided by the backend

> Groq does not itself fetch or inspect a GitHub repository from its URL. The backend must obtain and select repository content before sending it to the model. Keep repository access, prompt/context sizing, and API credentials in the backend; do not expose Groq keys to the frontend.

### Build plan (within the 48 hours)

1. Confirm the Groq model and account limits, then validate prompts using representative files from a test repo — **done**
2. Implement backend repository retrieval/context selection and the Groq client; keep model configuration in backend environment settings — **done**
3. Build the FastAPI backend: `POST /analyze-all` runs all 4 Groq capabilities concurrently and returns the full `OnboardingReport` in one shot; `POST /download` assembles all 6 sections into a `.md` file — **done**
4. Build the React frontend: input box for repo link → tabbed or sectioned report (Summary / Architecture / File Structure / Setup / Starter Tasks / Optimizations) → download button
5. Test end-to-end on your own **finance-tracker-api** repo as a real demo case — proves it works on genuine, non-trivial code
6. If time allows (hour 30+), consider an optional feature only after the core flow works; keep IBM watsonx integrations out of the core Groq path
7. Add a simple "before/after" framing for the demo: "onboarding this repo used to take ~2 days of reading → now takes 20 minutes"

### Demo/pitch angle

- Open with the real pain point: new devs (or even you, revisiting old code) waste hours just figuring out where things are
- Show the tool generating a guide live (or via recording) on the finance-tracker-api repo, hitting all 4 required capabilities
- End with the impact number: estimated time saved per new dev onboarded

## Confirmed Core Sections (frontend + export)

1. Repo analysis / summary
2. Architecture explanation + architecture diagram
3. File structure
4. Setup guidance
5. Starter task suggestions (beginner-friendly: small bugs, small reviews, small changes)
6. Optimization suggestions

## Export Feature: Download Report (Markdown only — PDF dropped)

Add a "Download" button on the frontend that exports all 6 sections above into a single `.md` file. PDF export was considered and intentionally dropped — not worth the added complexity/risk for a 48-hour build.

### Why Markdown

- Renders Mermaid diagrams natively on GitHub/GitLab/most MD viewers — no extra rendering work needed
- Keeps the whole export path to simple string templating — fewer moving parts to break during the hackathon

### Diagram approach

- When prompting Groq for the architecture explanation, ask it to ALSO output the diagram as **Mermaid syntax** (e.g. `graph TD; A-->B;`) in the same call — avoids a separate model request
- React frontend renders the Mermaid live on-screen using the `mermaid` JS library (lightweight, in-browser)
- MD export: FastAPI assembles all 6 sections (including the raw Mermaid code block) into one `.md` string, served as a file download

## Current Status

- **Person 1 (Groq Integration):** done — `backend/groq_client.py`, model `openai/gpt-oss-120b`, 4 keys with 8,000 TPM each, `_TpmThrottle` per key, `_sanitise_mermaid()` post-processor
- **Person 2 (Backend):** done — `POST /analyze-all` + `POST /download`, 22 passing tests, live end-to-end test validates real output from `finance-tracker-api`
- **Person 3 (Frontend):** pending — `frontend/` not yet created
- **Person 4 (Diagram + Export):** pending — backend download endpoint is ready; Mermaid frontend component not yet built
- **Person 5 (QA + Demo):** pending — blocked on frontend completion

## Next Steps

- Person 3: scaffold `frontend/` with Vite + React + TypeScript; build the input form, tabbed report display, and download button
- Person 4: integrate `mermaid` JS into the React app; build `MermaidDiagram` component; validate `/download` output on GitHub
- Person 5: end-to-end test once frontend is running; write README and demo script

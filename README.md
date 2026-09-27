# Smart Developer Onboarding Assistant

A web application that takes any public GitHub repository URL and generates a structured developer onboarding report using Groq AI — including a repo summary, architecture diagram, setup guide, starter tasks, and optimization suggestions.

Built for the **IBM Bob 2.0 Hackathon** (lablab.ai, Sept 25–27 2026).

---

## What it does

Paste a GitHub URL → get a full onboarding report in seconds.

| Section | What you get |
|---|---|
| **Repository Summary** | Plain-English overview of what the project does |
| **Architecture** | How the system is organized + a live Mermaid flowchart |
| **File Structure** | Every important file and its purpose |
| **Setup Guide** | Prerequisites, install steps, env vars, verification |
| **Starter Tasks** | Beginner-friendly first tasks grounded in the actual code |
| **Optimization Suggestions** | Practical improvements tied to real files |

All 4 Groq analysis calls run **in parallel** — one GitHub fetch, one wait, full report.

---

## Tech stack

| Layer | Technology |
|---|---|
| Backend | FastAPI + Python 3.11+ |
| AI | Groq API (`openai/gpt-oss-120b`) |
| GitHub fetch | `httpx` — async, no auth needed for public repos |
| Frontend | React + JavaScript (Vite) — `.jsx`, no TypeScript |

---

## API endpoints

### `POST /analyze-all`
Fetches the repository, runs all 4 Groq tools concurrently, returns the full report.

**Request**
```json
{ "repo_url": "https://github.com/owner/repo" }
```

**Response** — `OnboardingReport`
```json
{
  "analysis":    { "summary": "...", "file_structure": [...] },
  "architecture": { "explanation": "...", "mermaid": "flowchart LR ..." },
  "setup_guide": { "prerequisites": [...], "steps": [...], "environment_variables": [...], "verification": "..." },
  "starter_tasks_and_optimizations": { "starter_tasks": [...], "optimizations": [...] }
}
```

**Error codes**

| Code | Cause |
|---|---|
| `400` | Invalid or non-GitHub URL / no usable source files found |
| `503` | GitHub fetch failed (repo not found, network error) |
| `502` | Groq returned an unexpected response or keys are misconfigured |

---

### `POST /download`
Takes the `/analyze-all` response JSON (plus `repo_url`) and returns a `.md` file download containing all 6 report sections.

**Request** — spread the `/analyze-all` response and add `repo_url`:
```json
{
  "repo_url": "https://github.com/owner/repo",
  "analysis": { ... },
  "architecture": { ... },
  "setup_guide": { ... },
  "starter_tasks_and_optimizations": { ... }
}
```

**Response** — `onboarding-report.md` as a file attachment (`Content-Disposition: attachment`).

---

## Local setup

### Prerequisites

- Python 3.11 or higher
- A Groq account — get free API keys at https://console.groq.com/keys

---

### 1. Clone the repository

```bash
git clone <your-repo-url>
cd onboard.ai
```

---

### 2. Create and activate a virtual environment

```bash
# Windows
python -m venv .venv
.venv\Scripts\activate

# macOS / Linux
python -m venv .venv
source .venv/bin/activate
```

---

### 3. Install dependencies

```bash
pip install -r backend/requirements.txt
```

---

### 4. Configure environment variables

```bash
# Windows
copy backend\.env.example backend\.env

# macOS / Linux
cp backend/.env.example backend/.env
```

Open `backend/.env` and fill in your values:

```env
GROQ_MODEL=openai/gpt-oss-120b

GROQ_API_KEY1=gsk_xxxx   # analyze_repo
GROQ_API_KEY2=gsk_xxxx   # explain_architecture
GROQ_API_KEY3=gsk_xxxx   # generate_setup_guide
GROQ_API_KEY4=gsk_xxxx   # get_starter_tasks
```

> **Tip:** You can use the same key for all 4 entries. Using 4 separate keys gives each Groq call its own 8,000 TPM bucket so all 4 run truly in parallel without hitting rate limits.

---

### 5. Start the backend server

```bash
uvicorn backend.main:app --reload
```

Server starts at **http://127.0.0.1:8000**

Open **http://127.0.0.1:8000/docs** for the interactive Swagger UI.

---

### 6. Smoke test

```bash
curl -X POST http://127.0.0.1:8000/analyze-all \
  -H "Content-Type: application/json" \
  -d '{"repo_url": "https://github.com/aadarsh-create/finance-tracker-api"}'
```

Expect a `200` response with the full `OnboardingReport` JSON (~10–15 seconds for real Groq calls).

---

### 7. Set up and start the frontend

> **Prerequisites:** Node.js 18 or higher

```bash
cd frontend
npm install
npm run dev
```

Frontend starts at **http://localhost:5173**

Open it in your browser, paste a GitHub repo URL, and click **Analyze**.

> Both the backend (step 5) and frontend must be running at the same time.

---

## How it works

```
POST /analyze-all
  │
  ├─ parse_github_url()          validates the URL, extracts owner/repo
  ├─ fetch_repo_context()        fetches GitHub file tree, downloads source files
  │                              (capped at 20,000 chars, excludes secrets/binaries)
  │
  └─ GroqClient.analyze_all()   fires all 4 Groq calls concurrently via asyncio.gather
       ├─ analyze_repo()         → summary + file structure
       ├─ explain_architecture() → explanation + Mermaid diagram (sanitised)
       ├─ generate_setup_guide() → prerequisites, steps, env vars, verification
       └─ get_starter_tasks()    → starter tasks + optimization suggestions
            │
            └─ _TpmThrottle     per-key sliding-window rate limiter (8,000 TPM)

POST /download
  └─ assembles all 6 sections into a .md string → serves as file attachment
```

---

## Project structure

```
onboard.ai/
├── backend/
│   ├── main.py                  FastAPI app — CORS, router registration, .env loading
│   ├── groq_client.py           Async Groq wrapper — 4 capabilities + analyze_all()
│   ├── schemas.py               Pydantic request/response models for the API layer
│   ├── requirements.txt
│   ├── .env.example             Copy to .env and fill in your keys
│   ├── routers/
│   │   ├── analyze_all.py       POST /analyze-all
│   │   └── download.py          POST /download
│   └── services/
│       └── repo_context.py      GitHub fetch + context assembly
├── frontend/
│   ├── package.json
│   ├── vite.config.js
│   └── src/
│       ├── App.jsx              Root component — API call, state, error display
│       ├── App.css              Global styles
│       ├── main.jsx             ReactDOM entry point
│       └── components/
│           ├── RepoInputForm.jsx     URL input + submit button
│           ├── ReportTabs.jsx        6-tab navigation component
│           ├── DownloadButton.jsx    POST /download → .md file save
│           └── tabs/
│               ├── SummaryTab.jsx
│               ├── ArchitectureTab.jsx   Mermaid diagram placeholder
│               ├── FileStructureTab.jsx
│               ├── SetupTab.jsx
│               ├── StarterTasksTab.jsx
│               └── OptimizationsTab.jsx
└── README.md
```

---

## Environment variables reference

| Variable | Required | Description |
|---|---|---|
| `GROQ_MODEL` | ✅ | Groq model name, e.g. `openai/gpt-oss-120b` |
| `GROQ_API_KEY1` | ✅ | API key for `analyze_repo` |
| `GROQ_API_KEY2` | ✅ | API key for `explain_architecture` |
| `GROQ_API_KEY3` | ✅ | API key for `generate_setup_guide` |
| `GROQ_API_KEY4` | ✅ | API key for `get_starter_tasks` |

> Never commit `backend/.env` — it is git-ignored.

---

## Demo

Target repo used for testing: [`finance-tracker-api`](https://github.com/aadarsh-create/finance-tracker-api)

Sample output: a 14-file FastAPI + scikit-learn project fully onboarded in ~10 seconds — architecture diagram, complete setup steps, 5 starter tasks, 5 optimization suggestions.

**Before:** ~2 days reading code to understand a new repo
**After:** 20 minutes with a generated report

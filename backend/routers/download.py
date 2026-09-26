"""POST /download — assemble all report sections into a .md file download."""

from __future__ import annotations

from fastapi import APIRouter
from fastapi.responses import Response

from backend.schemas import DownloadRequest

router = APIRouter()


def _format_list(items: list[str]) -> str:
    return "\n".join(f"- {item}" for item in items)


@router.post("/download")
async def download(body: DownloadRequest) -> Response:
    a = body.analysis
    arch = body.architecture
    sg = body.setup_guide
    st = body.starter_tasks_and_optimizations

    # Build file structure section
    file_structure_lines = "\n".join(
        f"- `{f.path}` — {f.purpose}" for f in a.file_structure
    )

    # Build starter tasks section
    starter_task_lines = "\n".join(
        f"### {t.title}\n{t.description}\n\n**Files:** {', '.join(t.files)}"
        for t in st.starter_tasks
    )

    # Build optimizations section
    optimization_lines = "\n".join(
        f"### {o.suggestion}\n{o.rationale}\n\n**Files:** {', '.join(o.files)}"
        for o in st.optimizations
    )

    md = f"""\
# Developer Onboarding Report: {body.repo_url}

## 1. Repository Summary
{a.summary}

## 2. Architecture
{arch.explanation}

```mermaid
{arch.mermaid}
```

## 3. File Structure
{file_structure_lines}

## 4. Setup Guide

### Prerequisites
{_format_list(sg.prerequisites)}

### Steps
{_format_list(sg.steps)}

### Environment Variables
{_format_list(sg.environment_variables)}

### Verification
{sg.verification}

## 5. Starter Tasks
{starter_task_lines}

## 6. Optimization Suggestions
{optimization_lines}
"""

    return Response(
        content=md,
        media_type="text/markdown",
        headers={"Content-Disposition": 'attachment; filename="onboarding-report.md"'},
    )

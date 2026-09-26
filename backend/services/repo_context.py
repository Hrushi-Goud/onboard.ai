"""GitHub repository fetching and context assembly for Groq analysis."""

from __future__ import annotations

import os
import re
from urllib.parse import urlparse

import httpx

# Files/extensions to skip entirely
_EXCLUDED_EXTENSIONS = {
    ".env", ".key", ".pkl", ".db", ".csv", ".lock",
    ".png", ".jpg", ".jpeg", ".gif", ".svg", ".ico",
    ".woff", ".woff2", ".ttf", ".eot", ".otf",
    ".pdf", ".zip", ".tar", ".gz", ".exe", ".bin",
    ".pyc", ".so", ".dll", ".class",
}

_EXCLUDED_DIRS = {".git", "__pycache__", "node_modules", ".venv", "venv", "dist", "build"}

# Max bytes for a single file; max total context characters
_MAX_FILE_BYTES = 50_000
_MAX_CONTEXT_CHARS = 20_000

# Prefer source files when truncation is needed (lower = higher priority)
_SOURCE_PRIORITY = {".py", ".ts", ".tsx", ".js", ".jsx", ".go", ".rs", ".java", ".rb", ".php"}


def parse_github_url(url: str) -> tuple[str, str]:
    """Extract (owner, repo) from a GitHub URL.

    Accepts:
      https://github.com/owner/repo
      https://github.com/owner/repo.git
      https://github.com/owner/repo/tree/main
    """
    url = url.strip().rstrip("/")
    parsed = urlparse(url)
    if parsed.scheme not in ("http", "https"):
        raise ValueError(f"Invalid GitHub URL (bad scheme): {url!r}")
    if parsed.netloc not in ("github.com", "www.github.com"):
        raise ValueError(f"URL is not a GitHub URL: {url!r}")

    path = parsed.path.lstrip("/")
    # Remove trailing .git
    path = re.sub(r"\.git$", "", path)
    parts = path.split("/")
    if len(parts) < 2 or not parts[0] or not parts[1]:
        raise ValueError(f"Cannot extract owner/repo from URL: {url!r}")

    owner, repo = parts[0], parts[1]
    return owner, repo


async def fetch_repo_context(owner: str, repo: str) -> str:
    """Fetch a bounded plain-text context string from a public GitHub repository.

    Raises:
        ValueError: if the URL is invalid or no usable files are found.
        httpx.HTTPStatusError: if GitHub returns a non-2xx response.
    """
    api_base = f"https://api.github.com/repos/{owner}/{repo}"
    headers = {"Accept": "application/vnd.github+json", "X-GitHub-Api-Version": "2022-11-28"}

    async with httpx.AsyncClient(timeout=30.0) as client:
        # Fetch flat recursive file tree
        tree_resp = await client.get(f"{api_base}/git/trees/HEAD?recursive=1", headers=headers)
        tree_resp.raise_for_status()
        tree_data = tree_resp.json()

        blobs = [
            item for item in tree_data.get("tree", [])
            if item.get("type") == "blob"
        ]

        # Filter blobs
        candidates: list[tuple[int, dict]] = []
        for blob in blobs:
            path: str = blob.get("path", "")
            # Skip excluded dirs
            parts = path.split("/")
            if any(part in _EXCLUDED_DIRS for part in parts[:-1]):
                continue
            # Skip excluded extensions / dot-files that look like secrets
            _, ext = os.path.splitext(path)
            if ext.lower() in _EXCLUDED_EXTENSIONS:
                continue
            if os.path.basename(path).startswith(".env"):
                continue
            # Skip oversized files reported by tree
            size = blob.get("size", 0) or 0
            if size > _MAX_FILE_BYTES:
                continue
            # Priority: source files first, then other text files
            priority = 0 if ext.lower() in _SOURCE_PRIORITY else 1
            candidates.append((priority, blob))

        # Sort: source files first, then alphabetically
        candidates.sort(key=lambda x: (x[0], x[1]["path"]))

        if not candidates:
            raise ValueError(f"No usable source files found in {owner}/{repo}.")

        # Download files until we hit the context cap
        parts_collected: list[str] = []
        total_chars = 0

        for _, blob in candidates:
            if total_chars >= _MAX_CONTEXT_CHARS:
                break
            path = blob["path"]
            raw_url = f"https://raw.githubusercontent.com/{owner}/{repo}/HEAD/{path}"
            try:
                content_resp = await client.get(raw_url, headers={"Accept": "text/plain"})
                content_resp.raise_for_status()
                text = content_resp.text
            except (httpx.HTTPStatusError, httpx.RequestError):
                continue  # skip files we can't fetch

            if not text.strip():
                continue

            # Trim the individual file if needed
            remaining = _MAX_CONTEXT_CHARS - total_chars
            if len(text) > remaining:
                text = text[:remaining]

            block = f"{path}:\n{text}\n\n"
            parts_collected.append(block)
            total_chars += len(text)

    if not parts_collected:
        raise ValueError(f"No readable content found in {owner}/{repo}.")

    return "".join(parts_collected)

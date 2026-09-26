from __future__ import annotations

import asyncio
import json
from types import SimpleNamespace
from unittest.mock import AsyncMock

import pytest

from backend.groq_client import (
    ArchitectureExplanation,
    GroqClient,
    GroqConfigurationError,
    GroqResponseError,
    OnboardingReport,
    RepositoryAnalysis,
    SetupGuide,
    StarterTasksAndOptimizations,
)


def completion_with(content: str | None) -> SimpleNamespace:
    return SimpleNamespace(
        choices=[
            SimpleNamespace(message=SimpleNamespace(content=content)),
        ]
    )


def mock_sdk(monkeypatch: pytest.MonkeyPatch, response: SimpleNamespace) -> AsyncMock:
    create = AsyncMock(return_value=response)
    client = SimpleNamespace(
        chat=SimpleNamespace(
            completions=SimpleNamespace(create=create),
        ),
        close=AsyncMock(),
    )
    monkeypatch.setattr("backend.groq_client.AsyncGroq", lambda **_: client)
    return create


def build_client() -> GroqClient:
    return GroqClient(
        model="test-model",
        api_keys={
            "analyze_repo": "test-key-1",
            "explain_architecture": "test-key-2",
            "generate_setup_guide": "test-key-3",
            "get_starter_tasks": "test-key-4",
        },
    )


def test_analyze_repo_parses_typed_json(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    create = mock_sdk(
        monkeypatch,
        completion_with(
            '{"summary":"A small API","file_structure":'
            '[{"path":"main.py","purpose":"Starts the API"}]}'
        ),
    )

    result = asyncio.run(build_client().analyze_repo("main.py: FastAPI app"))

    assert isinstance(result, RepositoryAnalysis)
    assert result.summary == "A small API"
    assert result.file_structure[0].path == "main.py"
    assert create.await_args.kwargs["model"] == "test-model"


def test_architecture_request_includes_mermaid_in_single_call(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    create = mock_sdk(
        monkeypatch,
        completion_with(
            '{"explanation":"An HTTP request reaches the app",'
            '"mermaid":"flowchart TD\\n  Client --> App"}'
        ),
    )

    result = asyncio.run(
        build_client().explain_architecture("main.py: FastAPI app")
    )

    assert isinstance(result, ArchitectureExplanation)
    assert "flowchart TD" in result.mermaid
    assert create.await_count == 1


def test_setup_and_starter_task_shapes(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    create = mock_sdk(
        monkeypatch,
        completion_with(
            '{"prerequisites":["Python"],"steps":["Install dependencies"],'
            '"environment_variables":["DATABASE_URL"],"verification":"Run tests"}'
        ),
    )
    client = build_client()
    setup = asyncio.run(
        client.generate_setup_guide("requirements.txt: dependencies")
    )
    assert isinstance(setup, SetupGuide)
    assert setup.environment_variables == ["DATABASE_URL"]
    assert "actual FastAPI instance name" in create.await_args.kwargs["messages"][1][
        "content"
    ]

    create.return_value = completion_with(
        '{"starter_tasks":[{"title":"Add a test","description":"Cover a route",'
        '"files":["tests/test_api.py"]}],"optimizations":'
        '[{"suggestion":"Cache metadata","rationale":"Avoid repeated lookup",'
        '"files":["service.py"]}]}'
    )
    suggestions = asyncio.run(client.get_starter_tasks("service.py: API service"))

    assert isinstance(suggestions, StarterTasksAndOptimizations)
    assert suggestions.starter_tasks[0].files == ["tests/test_api.py"]
    assert suggestions.optimizations[0].suggestion == "Cache metadata"
    assert create.await_count == 2


def test_missing_model_fails_before_call() -> None:
    client = GroqClient(api_keys={"analyze_repo": "test-key"})

    with pytest.raises(GroqConfigurationError, match="GROQ_MODEL"):
        asyncio.run(client.analyze_repo("main.py: FastAPI app"))


def test_missing_method_api_key_is_reported() -> None:
    client = GroqClient(model="test-model", api_keys={})

    with pytest.raises(GroqConfigurationError, match="GROQ_API_KEY1"):
        asyncio.run(client.analyze_repo("main.py: FastAPI app"))


def test_empty_context_is_rejected() -> None:
    with pytest.raises(ValueError, match="must not be empty"):
        asyncio.run(build_client().analyze_repo("  "))


def test_invalid_model_response_raises_explicit_error(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    mock_sdk(monkeypatch, completion_with('{"unexpected":"shape"}'))

    with pytest.raises(GroqResponseError, match="RepositoryAnalysis schema"):
        asyncio.run(build_client().analyze_repo("main.py: FastAPI app"))


def test_empty_model_response_raises_explicit_error(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    mock_sdk(monkeypatch, completion_with(None))

    with pytest.raises(GroqResponseError, match="empty completion"):
        asyncio.run(build_client().analyze_repo("main.py: FastAPI app"))


def test_provider_errors_are_not_silently_swallowed(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    create = mock_sdk(monkeypatch, completion_with(None))
    create.side_effect = RuntimeError("provider unavailable")

    with pytest.raises(RuntimeError, match="provider unavailable"):
        asyncio.run(build_client().analyze_repo("main.py: FastAPI app"))


def test_analyze_all_runs_all_capabilities_concurrently(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    response_payloads = {
        "analyze_repo": {
            "summary": "Repository summary",
            "file_structure": [{"path": "main.py", "purpose": "Application entry point"}],
        },
        "explain_architecture": {
            "explanation": "Requests flow through the application.",
            "mermaid": "flowchart TD\n  Client --> App",
        },
        "generate_setup_guide": {
            "prerequisites": ["Python"],
            "steps": ["Install dependencies"],
            "environment_variables": [],
            "verification": "Start the API.",
        },
        "get_starter_tasks": {
            "starter_tasks": [],
            "optimizations": [],
        },
    }
    active_requests = 0
    max_active_requests = 0

    def build_mock_client(**_: str) -> SimpleNamespace:
        async def create(**kwargs: object) -> SimpleNamespace:
            nonlocal active_requests, max_active_requests
            active_requests += 1
            max_active_requests = max(max_active_requests, active_requests)
            try:
                await asyncio.sleep(0.02)
                prompt = kwargs["messages"][1]["content"]
                if not isinstance(prompt, str):
                    raise AssertionError("Expected the user prompt to be text.")
                operation = next(
                    name
                    for name in response_payloads
                    if name.replace("_", " ") in prompt.lower()
                    or {
                        "analyze_repo": "summarize the repository",
                        "explain_architecture": "explain the architecture",
                        "generate_setup_guide": "create local setup guidance",
                        "get_starter_tasks": "suggest beginner-friendly",
                    }[name]
                    in prompt.lower()
                )
                return completion_with(json.dumps(response_payloads[operation]))
            finally:
                active_requests -= 1

        return SimpleNamespace(
            chat=SimpleNamespace(
                completions=SimpleNamespace(create=create),
            ),
            close=AsyncMock(),
        )

    monkeypatch.setattr(
        "backend.groq_client.AsyncGroq",
        build_mock_client,
    )

    result = asyncio.run(build_client().analyze_all("main.py: FastAPI app"))

    assert isinstance(result, OnboardingReport)
    assert result.analysis.summary == "Repository summary"
    assert result.architecture.mermaid.startswith("flowchart TD")
    assert result.setup_guide.steps == ["Install dependencies"]
    assert max_active_requests == 4

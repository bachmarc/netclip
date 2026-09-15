"""Launcher-Tests für ``src/adapters/main.py`` (Story 03-01, Design §6).

Prüft nur ``build_app()``: ENV-Defaults und ENV-Override landen als Board-Limits in
``app.state.board``. Kein echter uvicorn-Start, kein Netz, kein Port — die App wird
nur gebaut und ihre Attribute werden inspiziert.
"""

from __future__ import annotations

from collections.abc import Callable  # noqa: F401 — Typ-Semantik für Reader
from datetime import UTC, datetime

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

from src.adapters.main import build_app
from src.core.board import PostBoard

DEFAULT_MAX_POSTS = 3000
DEFAULT_MAX_TEXT_LENGTH = 100_000
_NOW = datetime(2026, 1, 1, 12, 0, 0, tzinfo=UTC)  # deterministisch, keine Uhr im Test


def _build_app_clean_env(monkeypatch: pytest.MonkeyPatch) -> FastAPI:
    """Baut die App ohne MAX_POSTS/MAX_TEXT_LENGTH aus der System-ENV."""
    monkeypatch.delenv("MAX_POSTS", raising=False)
    monkeypatch.delenv("MAX_TEXT_LENGTH", raising=False)
    return build_app()


def _limits(board: PostBoard) -> tuple[int, int]:
    """Extrahiert die Board-Limits (deque-maxlen bzw. Textlimit)."""
    return board._posts.maxlen or 0, board._max_text_length


def test_build_app_ohne_env_nutzt_defaults(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Story 03-01: ohne ENV → Board-Defaults 3000/100000 in app.state.board."""
    app = _build_app_clean_env(monkeypatch)
    board = app.state.board
    assert isinstance(board, PostBoard)
    assert _limits(board) == (DEFAULT_MAX_POSTS, DEFAULT_MAX_TEXT_LENGTH)


def test_build_app_defaults_verhalten_fifo_und_textlimit(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Verhalten statt nur Attribute: FIFO-Limit und Textlimit greifen wirklich."""
    app = _build_app_clean_env(monkeypatch)
    board: PostBoard = app.state.board
    for _ in range(DEFAULT_MAX_POSTS + 1):
        board.add_post("x", "127.0.0.1", _NOW)
    assert len(board.get_posts()) == DEFAULT_MAX_POSTS
    with pytest.raises(ValueError):
        board.add_post("a" * (DEFAULT_MAX_TEXT_LENGTH + 1), "127.0.0.1", _NOW)


def test_build_app_env_override_max_posts(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """MAX_POSTS=5 aus ENV → Board-FIFO-Limit 5."""
    monkeypatch.delenv("MAX_TEXT_LENGTH", raising=False)
    monkeypatch.setenv("MAX_POSTS", "5")
    app = build_app()
    board: PostBoard = app.state.board
    assert _limits(board)[0] == 5
    for _ in range(6):
        board.add_post("x", "127.0.0.1", _NOW)
    assert len(board.get_posts()) == 5


def test_build_app_env_override_max_text_length(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """MAX_TEXT_LENGTH=10 aus ENV → Board-Textlimit 10."""
    monkeypatch.delenv("MAX_POSTS", raising=False)
    monkeypatch.setenv("MAX_TEXT_LENGTH", "10")
    app = build_app()
    board: PostBoard = app.state.board
    assert _limits(board)[1] == 10
    with pytest.raises(ValueError):
        board.add_post("a" * 11, "127.0.0.1", _NOW)


def test_build_app_env_override_beide_werte(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Beide ENV-Werte gleichzeitig → Board mit exakt diesen Limits (Story-Beispiel)."""
    monkeypatch.setenv("MAX_POSTS", "5")
    monkeypatch.setenv("MAX_TEXT_LENGTH", "10")
    app = build_app()
    assert _limits(app.state.board) == (5, 10)


def test_build_app_liefert_funktionale_app(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Gebaute App ist eine FastAPI-Instanz mit funktionsfähigen Routes (TestClient, kein Netz)."""
    app = _build_app_clean_env(monkeypatch)
    assert isinstance(app, FastAPI)
    client: TestClient = TestClient(app)
    response = client.get("/api/posts")
    assert response.status_code == 200
    assert response.json() == {"posts": [], "cleared": False}


def test_build_app_env_ignoriert_nicht_numerisch(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """int-Cast schlägt bei nicht-numerischem ENV-Wert fehl → bewusster Crash statt Stillhalter."""
    monkeypatch.setenv("MAX_POSTS", "nicht-eine-zahl")
    with pytest.raises(ValueError):
        build_app()
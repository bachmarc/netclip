"""NetClip Launcher (Design §6): baut die App aus ENV und startet uvicorn.

``build_app()`` ist der einzige Ort, der ENV liest (``MAX_POSTS``,
``MAX_TEXT_LENGTH``) und den Core konfiguriert — der HTTP-Adapter bleibt dünn.
``main()`` startet uvicorn (Konnektivität, nur hier, nie im Test-Pfad).
"""

from __future__ import annotations

import os

import uvicorn
from fastapi import FastAPI

from src.adapters.http import create_app
from src.core.board import PostBoard

DEFAULT_MAX_POSTS = 3000
DEFAULT_MAX_TEXT_LENGTH = 100_000
DEFAULT_PORT = "8000"


def build_app() -> FastAPI:
    """Liest Limits aus ENV (Defaults 3000/100000) und delegiert an ``create_app``."""
    max_posts = int(os.getenv("MAX_POSTS", str(DEFAULT_MAX_POSTS)))
    max_text_length = int(os.getenv("MAX_TEXT_LENGTH", str(DEFAULT_MAX_TEXT_LENGTH)))
    board = PostBoard(max_posts=max_posts, max_text_length=max_text_length)
    return create_app(board=board)


def main() -> None:
    """Startet uvicorn mit der ENV-konfigurierten App (host 0.0.0.0, PORT aus ENV)."""
    port = int(os.getenv("PORT", DEFAULT_PORT))
    uvicorn.run(build_app(), host="0.0.0.0", port=port)


if __name__ == "__main__":
    main()
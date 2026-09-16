"""NetClip HTTP-Adapter: dünne FastAPI-App um ``PostBoard`` (Design §1, §4, §5).

Jede Route ist dünn (3-10 Zeilen): Request-Extraktion → Core-Delegation → Antwort.
Keine Business-Logik hier — Validierung (leer/zu lang) bleibt vollständig im Core.
Kein Socket im Test-Pfad: ``fastapi.testclient.TestClient`` läuft ohne lauschenden Server.
"""

from __future__ import annotations

import json
from collections.abc import Callable
from datetime import UTC, datetime
from pathlib import Path

from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import HTMLResponse, JSONResponse

from src.core.board import PostBoard

_PLACEHOLDER_HTML = """<!DOCTYPE html>
<html lang="de">
<head><meta charset="utf-8"><title>NetClip</title></head>
<body><h1>NetClip – Frontend folgt</h1></body>
</html>"""


def _sender_ip(request: Request) -> str:
    """REQ-018, Design §1: echte Client-IP hinter Reverse-Proxy.

    Erste IP der ``X-Forwarded-For``-Kette (Client, Proxy, …); Fallback: TCP-Peer-IP.
    Vertrauensmodell LAN — XFF bei Direktzugriff fälschbar, IP-Anzeige informativ.
    """
    xff = request.headers.get("x-forwarded-for", "")
    if xff.strip():
        return xff.split(",")[0].strip()
    return request.client.host


def create_app(
    board: PostBoard | None = None,
    now_fn: Callable[[], datetime] | None = None,
) -> FastAPI:
    """Baut die FastAPI-App; ``board``/``now_fn`` injizierbar (deterministische Tests)."""
    board = board if board is not None else PostBoard()
    now_fn = now_fn if now_fn is not None else (lambda: datetime.now(UTC))

    app = FastAPI(title="NetClip")
    app.state.board = board

    @app.exception_handler(HTTPException)
    async def _http_error(
        _request: Request, exc: HTTPException
    ) -> JSONResponse:
        """Design §5: Fehlerformat ``{"error": <meldung>}`` statt FastAPI-Default."""
        return JSONResponse(status_code=exc.status_code, content={"error": exc.detail})

    @app.get("/", response_class=HTMLResponse)
    def root() -> str:
        """Liefert ``src/web/index.html`` falls vorhanden, sonst HTML-Platzhalter."""
        index = Path(__file__).resolve().parents[1] / "web" / "index.html"
        if index.is_file():
            return index.read_text(encoding="utf-8")
        return _PLACEHOLDER_HTML

    @app.get("/api/posts")
    def get_posts(since_id: int = 0) -> dict:
        """Posts mit ``id > since_id`` plus Clear-Version (REQ-019, alle Clients)."""
        return {
            "posts": board.get_posts(since_id=since_id),
            "clear_version": board.clear_version,
        }

    @app.post("/api/posts")
    async def add_post(request: Request) -> dict:
        """Fügt Post hinzu; delegiert Validierung an Core (ValueError → 400)."""
        try:
            body = await request.json()
        except json.JSONDecodeError as exc:
            raise HTTPException(
                status_code=400, detail="Ungültiges JSON im Body."
            ) from exc
        text = body.get("text") if isinstance(body, dict) else None
        if not isinstance(text, str):
            raise HTTPException(
                status_code=400, detail='Body muss {"text": str} enthalten.'
            )
        try:
            return {"post": board.add_post(text, _sender_ip(request), now_fn())}
        except ValueError as exc:
            raise HTTPException(status_code=400, detail=str(exc)) from exc

    @app.post("/api/clear")
    async def clear(request: Request) -> dict:
        """Cleared Board (mode ``all``/``last``); ungültiger Mode/Body → 400."""
        try:
            body = await request.json()
        except json.JSONDecodeError as exc:
            raise HTTPException(
                status_code=400, detail="Ungültiges JSON im Body."
            ) from exc
        mode = body.get("mode") if isinstance(body, dict) else None
        if mode == "all":
            board.clear_all()
        elif mode == "last":
            board.clear_last()
        else:
            raise HTTPException(
                status_code=400, detail="mode muss 'all' oder 'last' sein."
            )
        return {"cleared": True}

    return app

# Story 02-01 — FastAPI-Adapter (API)

Status: Geplant
Traceability: REQ-001, REQ-003, REQ-009, REQ-012 → Design §1 (Adapter), §4 (API-Skizze), §5 (Fehlerbehandlung)

## Definition

Dünner HTTP-Adapter um `PostBoard` (aus 01-01, gemerged): 4 Routen nach Design §4.
Alle Entscheidungen delegiert an Core; Adapter extrahiert nur Request-Daten und mapped Fehler.

## Entwicklungsziel

HTTP-API vollständig nutzbar: Seite ausliefern, Posts lesen (Cursor), Post senden, Clear.
Testbar ohne echten Socket via FastAPI `TestClient`.

## Developer Targets (exakt, nicht mehr/nicht weniger)

- [ ] `src/adapters/http.py` — Factory nach Design §1:
      - `create_app(board: PostBoard | None = None, now_fn: Callable[[], datetime] | None = None) -> FastAPI`
        — Defaults: `PostBoard()`, `lambda: datetime.now(timezone.utc)`; Board zusätzlich in `app.state.board`
      - `GET /` — liefert `src/web/index.html` falls vorhanden; sonst Platzhalter-HTML
        „NetClip – Frontend folgt" (ermöglicht Parallelarbeit mit 02-02)
      - `GET /api/posts` — Query `since_id: int = 0`; Antwort `{"posts": [...], "cleared": board.consume_cleared()}`
      - `POST /api/posts` — Body `{"text": str}`; `ValueError` aus Core → HTTP 400 mit
        `{"error": <deutsche Meldung>}`; Erfolg → `{"post": {...}}` (Status 200)
      - `POST /api/clear` — Body `{"mode": "all"|"last"}`; ungültiger `mode`/Body → HTTP 400;
        Erfolg → `{"cleared": true}`
      - Client-IP via `request.client.host` als `sender`
      - Jede Route: 3-10 Zeilen (Extraktion → Delegation → Antwort)
- [ ] `tests/test_http_adapter.py` — mit `fastapi.testclient.TestClient` (kein Socket, kein Netz):
      - `POST /api/posts` → 200, Post-Dict mit `sender="testclient"` in Liste sichtbar
      - Leerer Text → 400; Text > Limit (kleines `PostBoard(max_text_length=5)` injizieren) → 400 mit Fehlermeldung
      - `GET /api/posts?since_id=1` → nur neuere Posts
      - `POST /api/clear mode=all` → danach `GET /api/posts` liefert `cleared: true` (genau einmal), leere Liste
      - `POST /api/clear mode=last` → letzter Post weg
      - `POST /api/clear mode=bogus` → 400
      - `GET /` → 200 (HTML — Inhalt egal, Frontend kommt in 02-02)
      - Deterministische Zeit: `now_fn=lambda: datetime(2026,1,1,12,0, tzinfo=timezone.utc)` injizieren,
        Timestamp im Post prüfen
      - Board-Injektion: eigenes `PostBoard` übergeben und in `app.state.board` wiederfinden

## Akzeptanzkriterien (prüft QA-Manager)

- [ ] `pytest` grün (Adapter-Tests + Core-Tests)
- [ ] Routen entsprechen Design §4 (Pfade, Bodies, Statuscodes, Fehlerformate)
- [ ] Adapter-Methoden dünn (kein Business-Logic-Duplikat — Validierung liegt im Core)
- [ ] Kein Netzwerk im Test-Pfad (`TestClient`, kein `uvicorn.run` in Tests)
- [ ] `ruff check .` ohne Fehler

## Testkriterien (müssen VOR Implementierung existieren)

- [ ] `tests/test_http_adapter.py` nutzt `TestClient` + injiziertes `PostBoard`/`now_fn` — läuft
      ohne lauschenden Server, ohne externe Systeme (Fake = TestClient-Transport)
- [ ] Alle Fehlerfälle (400) sind als Tests VOR der Implementierung definiert
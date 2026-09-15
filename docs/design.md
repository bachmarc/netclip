# Design — NetClip (LAN-Zwischenablage)

> Source of Truth, freigegeben im Dialog (Phase 1).

## 1. Architektur: Funktion vs Konnektivität

Strikte Trennung (Muster: `intesis_modbus/CLAUDE.md`):

### `src/core/` — Funktion (reine Logik)

- **Null Imports** aus Framework/IO/HTTP/DB — nur `collections`, `dataclasses`, `typing`.
- Bekommt alles als Parameter (inkl. `now` → deterministische Tests), gibt Dicts/Primitives zurück.
- Vollständig unit-testbar.

**`src/core/board.py` — Klasse `PostBoard`:**

```python
class PostBoard:
    def __init__(self, max_posts: int = 3000, max_text_length: int = 100_000) -> None: ...
    def add_post(self, text: str, sender: str, now: datetime) -> dict:
        """Neuen Post anlegen. Validiert Länge (leer/zu lang → ValueError). Gibt Post-Dict zurück."""
    def clear_all(self) -> None: ...
    def clear_last(self) -> None: ...
    def get_posts(self, since_id: int = 0) -> list[dict]:
        """Posts mit id > since_id, aufsteigend. since_id=0 → alle."""
    def simuliere_post(self, text: str = "test") -> dict:
        """Test-Helper: fügt Post mit deterministischer Zeit/IP hinzu."""
```

- Speicher: `deque(maxlen=max_posts)` + monotoner ID-Counter.
- Post-Dict: `{"id": int, "text": str, "timestamp": ISO-8601-UTC, "sender": str}`.
- Fehler via `ValueError` mit klaren Meldungen — Adapter mapped auf HTTP-Status.

### `src/adapters/` — Konnektivität (dünne Wrapper)

**`src/adapters/http.py` — FastAPI-App (3-10 Zeilen pro Route):**

- Extrahiert Text aus Request-Body, Client-IP aus Request, delegiert an `PostBoard`.
- `now` wird im Adapter geholt (z.B. `datetime.now(UTC)`) — Core bleibt rein.
- Mapping: `ValueError` → HTTP 400 mit Meldung.
- **Timer/Listener ausschließlich hier** — hier: keiner nötig (RAM-only, kein Auto-Clear).

**`src/web/index.html`** — statische Seite (kein Build-Step, pures HTML+JS):
Textfeld, Buttons „Senden", „Clear all", „Clear last"; Post-Liste (neueste oben);
Polling per `fetch` alle 2 s mit `since_id`; Anzeige Zeit + IP (Deutsch formatiert).

## 2. Fake-Interfaces (PFLICHT)

| Externes System | Fake | Ort |
|-----------------|------|-----|
| Systemuhr | `FakeClock` (deterministisch, tick-bar) | `tests/fakes/fake_clock.py` |
| HTTP-Transport | FastAPI `TestClient` (kein Socket) | `tests/test_http_adapter.py` |

- Core-Tests laufen komplett ohne FastAPI/Netz — nur `PostBoard` + `FakeClock`.
- Adapter-Tests laufen ohne echten Socket via `TestClient`.
- Ist Core nicht ohne Fakes testbar → Designfehler.

## 3. Datenmodell (RAM-only)

```
PostBoard
├── posts: deque[dict] (maxlen = MAX_POSTS, default 3000)
├── next_id: int (monoton, restartet mit Prozess)
└── Post = {id: int, text: str, timestamp: ISO-8601-UTC, sender: str (IP)}
```

Keine Datenbank, keine Dateien, keine Session. Restart = leer (REQ-007).

## 4. API-Skizze

| Route | Methode | Body/Query | Antwort | Fehler |
|-------|---------|-----------|---------|--------|
| `/` | GET | — | `index.html` | — |
| `/api/posts` | GET | `?since_id=<int>` (optional) | `{"posts": [...], "cleared": bool}` | — |
| `/api/posts` | POST | `{"text": str}` | `{"post": {...}}` | 400: leer / zu lang |
| `/api/clear` | POST | `{"mode": "all"\|"last"}` | `{"cleared": true}` | 400: ungültiger mode |

**Clear-Signalisierung:** Jedes `clear` setzt intern ein Cleared-Flag; `GET /api/posts`
liefert `cleared: true`, wenn seit letztem Abruf gecleart wurde → Client leert seine Liste.
`since_id`-Cursor danach zurücksetzen (nächster Abruf: `since_id=0`).

## 4a. Frontend-Verhalten (Polling)

- Initial: `GET /api/posts` (alles), merken `last_id`.
- Poll alle 2 s: `GET /api/posts?since_id=last_id`.
  - `cleared: true` → Liste leeren, `last_id = 0`.
  - Sonst neue Posts oben einfügen, `last_id` aktualisieren.
- Absenden/„Clear"-Buttons → `POST` → sofortiger Poll (kein Warten aufs Intervall).

## 5. Fehlerbehandlung

- Leerer Text / > `max_text_length` → `ValueError` im Core → HTTP 400 mit deutscher Meldung.
- Ungültiger Clear-Mode → HTTP 400.
- Keine globale State-Recovery nötig (RAM-only; Crashes verlieren Daten — akzeptiert per Requirements).

## 6. Deployment

- **Dockerfile**: `python:3.12-slim`, `pip install -r requirements.txt`, `CMD uvicorn`.
- **docker-compose.yml**: Port `8000:8000` (via ENV `PORT`), `MAX_POSTS`, `MAX_TEXT_LENGTH` als ENV.
- **GitHub Actions** (`.github/workflows/ci.yml`): Jobs `pytest` + `ruff check`, Docker-Build (kein Push ohne Registry-Secret).
- ENV-Konfig: `PORT` (default 8000), `MAX_POSTS` (3000), `MAX_TEXT_LENGTH` (100000).

## 7. Versionierung

- `src/version.py` → `APP_VERSION = "0.1.0"`, Semantic Versioning.
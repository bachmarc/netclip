# Story 01-01 — Core: FakeClock + PostBoard

Status: Geplant
Traceability: REQ-002, REQ-004, REQ-005, REQ-006, REQ-007, REQ-010, REQ-011 → Design §1 (Core), §3 (Datenmodell)

## Definition

Vollständige, reine Kernlogik des Boards: Posts anlegen/validieren, abrufen (mit `since_id`-Cursor),
Clear all / Clear last, FIFO-Limit, Clear-Signal. **Null Framework-Imports** — nur stdlib
(`collections`, `dataclasses` optional, `typing`). Zeit kommt als Parameter (`now`).

## Entwicklungsziel

Alle Post/Read/Clear-Regeln sind implementiert und **vollständig ohne FastAPI/Netz** getestet.

## Developer Targets (exakt, nicht mehr/nicht weniger)

- [ ] `tests/fakes/fake_clock.py` — **zuerst** schreiben:
      `FakeClock` mit `now() -> datetime` (UTC), startet bei `2026-01-01T12:00:00+00:00`,
      Methode `tick(seconds=1)` rückt Zeit vor; Konstruktor `FakeClock(start: datetime | None = None)`
- [ ] `src/core/board.py` — Klasse `PostBoard` exakt nach Design §1:
      - `__init__(self, max_posts: int = 3000, max_text_length: int = 100_000)`
      - `add_post(text, sender, now) -> dict` — `ValueError` bei leerem/nur-Whitespace-Text
        und bei `len(text) > max_text_length` (deutsche Meldungen); Post-Dict:
        `{"id": int, "text": str, "timestamp": ISO-8601-UTC, "sender": str}`
      - `get_posts(since_id: int = 0) -> list[dict]` — Posts mit `id > since_id`, aufsteigend
      - `clear_all()`, `clear_last()` — beide setzen Clear-Signal
      - `consume_cleared() -> bool` — `True` genau einmal nach Clear, danach wieder `False`
      - `simuliere_post(text="test", sender="test-ip", now=None) -> dict` — Helper, nutzt
        `FakeClock`-Default-Zeit `2026-01-01T12:00:00+00:00`, falls `now=None`
      - Speicher: `collections.deque(maxlen=max_posts)`; ID-Counter monoton ab 1;
        bei `max_posts`-Überlauf fliegt automatisch der älteste Post raus (FIFO)
- [ ] `tests/test_board.py` — Unit-Tests (nur `PostBoard` + `FakeClock`, keine FastAPI-Imports):
      - Add: Post erscheint mit id=1, aufsteigende IDs, `timestamp`/`sender` korrekt übernommen
      - Add-Validierung: leerer Text → `ValueError`; nur Whitespace → `ValueError`;
        Text > `max_text_length` → `ValueError` (Meldung prüfen: enthält „100000"/Grenzwert)
      - `get_posts()`: komplett; `get_posts(since_id=1)` → nur Posts 2+; `since_id=0` → alle
      - Clear all: Liste leer, `consume_cleared()` erst `True`, dann `False`
      - Clear last: nur letzter Post weg, Clear-Signal ebenfalls gesetzt
      - FIFO: Board mit `max_posts=3`, 5 Adds → nur IDs 3,4,5 vorhanden
      - `simuliere_post()`: funktioniert ohne Argumente, deterministische Werte
      - RAM-only/Restart-Semantik: neues `PostBoard()` ist leer (REQ-007)

## Akzeptanzkriterien (prüft QA-Manager)

- [ ] `pytest` grün (alle Board-Tests)
- [ ] `src/core/board.py` hat **keine** Imports aus fastapi/http/uvicorn/netz/io (nur stdlib)
- [ ] Alle REQ-002/004/005/006/007/010/011-Regeln durch Tests abgedeckt
- [ ] `ruff check .` ohne Fehler

## Testkriterien (müssen VOR Implementierung existieren)

- [ ] `tests/fakes/fake_clock.py` existiert VOR `src/core/board.py`
- [ ] Alle Tests laufen ohne echten Server, ohne FastAPI, ohne Netz — nur Core + Fake
- [ ] Zeit deterministisch via `FakeClock` (kein `datetime.now()` im Test-Pfad)
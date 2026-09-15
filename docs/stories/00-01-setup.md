# Story 00-01 — Projekt-Setup (Infrastruktur)

Status: Geplant
Traceability: NFR-004 → Design §7

## Definition

Infrastruktur-Grundlage für alle Folge-Stories: Paket-Metadaten, Test-Setup, Version-Modul.
Kein anwendungslogisches Verhalten, keine Implementierung von Core/Adaptern.

## Entwicklungsziel

Jede Folge-Story kann direkt `pytest`, Import-Pfade und `APP_VERSION` nutzen, ohne Setup-Konflikte.

## Developer Targets (exakt, nicht mehr/nicht weniger)

- [ ] `pyproject.toml` — Projektname `netclip`, Python `>=3.12` (`requires-python`),
      `[tool.pytest.ini_options]` mit `testpaths = ["tests"]`,
      `[tool.ruff]` mit `line-length = 100`
- [ ] `requirements.txt` — exakt: `fastapi`, `uvicorn[standard]`, `pytest`, `httpx`, `ruff`
- [ ] `src/__init__.py`, `src/core/__init__.py`, `src/adapters/__init__.py`, `tests/__init__.py`, `tests/fakes/__init__.py` — leer (nur Existenz)
- [ ] `src/version.py` — `APP_VERSION = "0.1.0"`
- [ ] `tests/conftest.py` — leer (Platzhalter für künftige Fixtures)
- [ ] `tests/test_version.py` — ein Test: importiert `src.version.APP_VERSION`,
      assert `== "0.1.0"` (schützt gegen versehentliche Versions-Bumps)

## Akzeptanzkriterien (prüft QA-Manager)

- [ ] `pytest` läuft grün (1 Test)
- [ ] `ruff check .` läuft ohne Fehler (Konfiguration vorhanden)
- [ ] `python -c "from src.version import APP_VERSION"` funktioniert vom Repo-Root
- [ ] Alle `__init__.py` existieren (Import-Pfade nutzbar)

## Testkriterien (müssen VOR Implementierung existieren)

- [ ] `tests/test_version.py` testet nur `src.version.APP_VERSION` — keine externen Systeme,
      kein Netzwerk, kein Server. Reine Import-Assertion.
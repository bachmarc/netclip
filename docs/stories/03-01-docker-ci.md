# Story 03-01 — Docker + GitHub Actions CI

Status: Geplant
Traceability: NFR-001, NFR-003 → Design §6 (Deployment), §7 (Versionierung)

## Definition

Deployment & CI: Dockerfile, docker-compose, GitHub Actions Workflow. Keine Änderungen an
Core/Adapter/Frontend — nur Verpackung und Pipeline.

## Entwicklungsziel

`docker compose up` startet NetClip auf `http://<host>:8000`; CI läuft bei jedem Push
(pytest + ruff + Docker-Build).

## Developer Targets (exakt, nicht mehr/nicht weniger)

- [ ] `src/adapters/main.py` — exakt nach Design §6:
      `build_app() -> FastAPI` (liest `MAX_POSTS`, `MAX_TEXT_LENGTH` aus ENV mit Defaults 3000/100000)
      und `main()` mit `uvicorn.run(build_app(), host="0.0.0.0", port=int(os.getenv("PORT", 8000)))`;
      `if __name__ == "__main__": main()`
- [ ] `tests/test_main_launcher.py` — mit monkeypatch:
      - `build_app()` ohne ENV → Board-Defaults (3000/100000) in `app.state.board` prüfen
      - `os.environ["MAX_POSTS"]="5"`, `os.environ["MAX_TEXT_LENGTH"]="10"` → `build_app()`
        liefert Board mit diesen Limits
- [ ] `Dockerfile` — nach Design §6: `python:3.12-slim`, `WORKDIR /app`, `COPY` von
      `requirements.txt` + `src/`, `pip install -r requirements.txt`, non-root User
      (`useradd` + `USER`), `EXPOSE 8000`, `CMD ["python", "-m", "src.adapters.main"]`
- [ ] `.dockerignore` — `__pycache__`, `.git`, `tests/`, `docs/`, `.venv`, `.mypy_cache`, `.pytest_cache`
- [ ] `docker-compose.yml` — Service `netclip`: Build aus `.`, Port `8000:8000`,
      ENV `PORT`, `MAX_POSTS`, `MAX_TEXT_LENGTH` (Defaults in Compose-Werten), `restart: unless-stopped`
- [ ] `.github/workflows/ci.yml` — Workflow `CI`, Trigger `push` + `pull_request`,
      Jobs: (1) `lint-test`: `pip install -r requirements.txt`, `ruff check .`, `pytest` — Python 3.12;
      (2) `docker-build`: `docker build .` (kein Push ohne Registry-Secret)
- [ ] `README.md` — Betrieb-Sektion aktualisieren: Docker-Start, ENV-Tabelle bleibt korrekt

## Akzeptanzkriterien (prüft QA-Manager)

- [ ] `pytest` grün (inkl. Launcher-Tests), `ruff check .` ohne Fehler
- [ ] `docker build .` erfolgreich (lokal verifizierbar); Image startet und `GET /` antwortet (manueller SMOKE)
- [ ] CI-YAML syntaktisch valide (z.B. `python -c "import yaml; yaml.safe_load(open('.github/workflows/ci.yml'))"` oder `actionlint` falls verfügbar)
- [ ] Dockerfile: non-root User, keine Secrets im Image, keine unnötigen Layer
- [ ] Core/Adapter/Frontend-Dateien unverändert (nur Deployment-Additionen + README)

## Testkriterien (müssen VOR Implementierung existieren)

- [ ] `tests/test_main_launcher.py` definiert ENV-Default- und ENV-Override-Fälle VOR Implementierung,
      nutzt nur `monkeypatch` + `TestClient` — kein echter uvicorn-Start, kein Netz
- [ ] Docker/CI selbst sind nicht unit-testbar → Verifikation via Build-SMOKE + YAML-Validierung
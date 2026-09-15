# AGENTS.md — Repo-Leitplanken (NetClip)

Dieses Dokument definiert Leitplanken für alle Agenten (architect, developer, qa-manager) in diesem Repo.

## Projekt: NetClip (LAN-Zwischenablage)

- **Stack**: Python 3.12, FastAPI + uvicorn, statisches HTML/JS-Frontend, Docker.
- **Kernregel**: `src/core/board.py` (`PostBoard`) kennt kein FastAPI, kein HTTP, keine Uhr.
  Zeit kommt als Parameter (`now`), Konfiguration (`max_posts`, `max_text_length`) per Konstruktor.
- **RAM-only**: Keine Persistenz, keine Auto-Clear-Timer (nur manuelles Clear all / Clear last).
- UI-Texte Deutsch, Code/Bezeichner Englisch.

## Architektur: Funktion vs Konnektivität

Strikte Trennung (Muster: `intesis_modbus/CLAUDE.md`):

- **`src/core/`** — reine Logik/Algorithmen.
  - **Null Imports** aus Framework/IO/HA/DB/API.
  - Bekommt alle Daten als Parameter, gibt Dicts/Primitives zurück.
  - Vollständig unit-testbar, enthält Simulation-Helper (`simuliere_post()`).
- **`src/adapters/`** — dünne Wrapper (3-10 Zeilen pro Methode).
  - Extrahiert Request-Daten, **delegiert alle Entscheidungen an Core**, gibt HTTP-Antwort.
  - Timer/Listener/Scheduler ausschließlich hier.
- **Fakes sind Pflicht** für jede externe Abhängigkeit: `tests/fakes/`.
  - Core-Tests laufen **ohne** echte Systeme (`FakeClock`, FastAPI `TestClient` statt Sockets).
  - Ist Core nicht ohne Fakes testbar → Designfehler.

## Git-Konvention

- Jede Story = eigener Branch: `feature/<story-id>-<slug>` (z.B. `feature/01-02-cards-crud`).
- **Worktree-Pflicht:** Jede Developer-Session arbeitet in einem eigenen Git-Worktree
  `.worktrees/<story-id>-<slug>/` (angelegt vom architect). Das Hauptverzeichnis bleibt
  **immer auf `main`** (Merges, Hygiene). Zwei Agenten teilen NIE ein Working Directory.
- **Kein direkter Push auf `main`.** Merge nur nach QA-Gate (PASS).
- Commit-Body enthält Metadaten für QA-Requeue:
  ```
  symbols: <geänderte Export-Symbols> | breaks: <none|breaking> | affects: <abhängige Files> | tests: <pytest-Ergebnis>
  ```

## Workflow

1. **Stories**: `STORIES.md` (Index) + `docs/stories/<phase>-<id>-<slug>.md`.
   Jede Story verlinkt Traceability (`REQ-XXX` + Design-Abschnitt) und enthält
   **Testkriterien, die VOR Implementierung existieren (Fake-basiert)**.
2. **Developer**: implementiert GENAU die Developer Targets — nichts mehr, nichts weniger.
   Tests zuerst schreiben, `pytest` muss grün sein.
3. **QA-Gate**: prüft Requirements, Tests, Architektur-Trennung, Fake-Nutzung.
   PASS → Merge. FAIL → Fix-Loop (max. 3), dann BLOCKED → zurück an architect/User.

## Sprachen

- Dialog mit User: Deutsch
- Code/Bezeichner: Englisch
- UI-Texte: Deutsch

## Verbote

- Kein autonomes Dekomponieren/Implementieren außerhalb freigegebener Stories.
- Keine unangefragten Features außerhalb der Developer Targets.
- Keine Imports von IO/Framework in `src/core/`.
- Kein `git init`/Schreiben außerhalb des Projekt-Pfads.

## Referenzen

- `intesis_modbus/CLAUDE.md` — Architektur-Trennung, Simulation-Tests
- `vokabel/AGENTS.md` + `vokabel/STORIES.md` — Story-Workflow
- `docs/requirements.md`, `docs/design.md` — Source of Truth (nach Phase 1)
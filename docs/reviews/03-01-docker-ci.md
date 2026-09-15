# QA-Review — Story 03-01-docker-ci

- **Datum:** 2026-09-15
- **QA-Manager:** QA-Gatekeeper
- **Branch:** `feature/03-01-docker-ci` (Commit `d341549`, Merge-Base `d38c912`)
- **Urteil:** ✅ **PASS** — Freigabe für Merge nach `main` (Merge durch architect nach User-Go;
  `docker build` + SMOKE gemäß Anweisung architect-seitig nach Merge, s. Bewertung 3)

## Geprüfte Punkte

| Prüfpunkt | Ergebnis |
|-----------|----------|
| `pytest` grün (Erwartung 44 = 37 + 7 Launcher-Tests) | ✅ `44 passed, 1 warning in 0.72s` (Board 20, HTTP-Adapter 16, Launcher 7, Version 1) |
| `ruff check .` ohne Fehler | ✅ `All checks passed!` |
| `main.py`: `build_app()` ENV-Defaults 3000/100000 + int-Cast | ✅ `DEFAULT_MAX_POSTS = 3000`, `DEFAULT_MAX_TEXT_LENGTH = 100_000`, `int(os.getenv(...))` |
| `main.py`: host `0.0.0.0`, `PORT`-Default 8000 | ✅ `uvicorn.run(build_app(), host="0.0.0.0", port=int(os.getenv("PORT", "8000")))` |
| `main.py`: `if __name__ == "__main__": main()` | ✅ vorhanden |
| Dockerfile: `python:3.12-slim`, `WORKDIR /app`, Layer-Reihenfolge (requirements vor Code) | ✅ COPY requirements.txt+pyproject.toml → pip install → COPY src/ → EXPOSE → CMD |
| Dockerfile: non-root User | ✅ `useradd --create-home netclip` + `USER netclip` |
| Dockerfile: keine Secrets, keine unnötigen Layer | ✅ keine Secrets; Layer minimal (2× RUN) — s. Beobachtung 3 |
| Dockerfile: `CMD ["python", "-m", "src.adapters.main"]` | ✅ Modulpfad aus `/app` auflösbar (`python -m` + CWD) |
| .dockerignore: mind. die geforderten Einträge | ✅ `__pycache__/`, `*.py[cod]`, `.git/`, `tests/`, `docs/`, `.worktrees/`, `.venv/`, `.mypy_cache/`, `.pytest_cache/`, `.ruff_cache/` + sinnvolle Extras |
| docker-compose.yml: service/build/ports/ENV/restart | ✅ `netclip`, `build: .`, `"8000:8000"`, ENV `PORT=8000`/`MAX_POSTS=3000`/`MAX_TEXT_LENGTH=100000`, `restart: unless-stopped` |
| ci.yml: name CI, Trigger push + pull_request | ✅ |
| ci.yml: Job `lint-test` (Python 3.12, pip install, ruff, pytest) | ✅ `setup-python 3.12`, `ruff check .`, `pytest -q`; ruff/pytest/httpx in `requirements.txt` → CI lauffähig |
| ci.yml: Job `docker-build` (build, kein Push) | ✅ `docker build .`, kein Registry-Secret, kein Push |
| README-Betriebs-Sektion: Docker-Start + ENV-Tabelle konsistent mit Code-Defaults | ✅ `docker compose up` + ENV 8000/3000/100000 = `main.py`-Defaults = Compose-Werte |
| YAML syntaktisch valide | ✅ beide Dateien via `yaml.safe_load` geparst (s. Beobachtung 4: `on:` → PyYAML-`True`-Quirk) |
| Developer Targets: diff enthält NUR die 7 Target-Dateien | ✅ `git diff d38c912..d341549 --stat`: exakt `.dockerignore`, `.github/workflows/ci.yml`, `Dockerfile`, `README.md`, `docker-compose.yml`, `src/adapters/main.py`, `tests/test_main_launcher.py` |
| Launcher-Tests: ENV-Default + ENV-Override via monkeypatch | ✅ 7 Tests: Defaults (2×, inkl. Verhaltenstest FIFO/Textlimit), Override max_posts/max_text_length/beide (3×), funktionale App via TestClient (1×), int-Cast-Crash bei nicht-numerisch (1×) |
| KEIN echter uvicorn-Start/Port/Netz in tests/ | ✅ grep: nur Docstring-Erwähnung; `main()` wird nie aufgerufen; `uvicorn.run` 0 Code-Treffer |
| Core/Adapter/Frontend/bestehende Tests unverändert | ✅ `git diff` auf `src/core/`, `src/adapters/http.py`, `src/web/`, Bestands-Tests: 0 Änderungen |
| Architektur-Trennung | ✅ Launcher in `src/adapters/` (Framework-Imports erlaubt, dünner Kompositions-Root: delegiert an `create_app`); Core unangetastet, kennt kein ENV/uvicorn |
| Commit-Konvention + Body-Metadaten | ✅ `feat(03-01): docker + github actions ci` + `symbols/breaks/affects/tests` + red-Notiz |
| Branch-Hygiene: 1 Commit auf Merge-Base, kein Story-Mix, sauberes Workdir | ✅ `git log main..HEAD`: nur `d341549`; `git merge-tree`: konfliktfrei |

## Bewertung der gemeldeten Abweichungen

1. **monkeypatch statt os.environ-Direktzuweisung — OK, keine Abweichung.**
   Die Story-Testkriterien schreiben monkeypatch zwingend vor („nutzt nur monkeypatch +
   TestClient"). `monkeypatch.setenv("MAX_POSTS", "5")` erreicht exakt den in den
   Developer-Targets beschriebenen ENV-Zustand, plus automatisches Cleanup und via
   `delenv` garantiert saubere Default-Tests (System-ENV kann Tests nicht verschmutzen).
   Better practice als Direktzuweisung — so gewollt.
2. **`Callable`-Import mit `noqa` (tests/test_main_launcher.py:10) — Ballast, harmlos.**
   Unbenutzter Import, kein Verhaltenseinfluss, ruff-konform durch noqa. Empfehlung: in
   einem Folge-Commit entfernen. Kein FAIL-Grund.
3. **docker build nicht ausgeführt — OK gemäß Anweisung.** QA führt keinen Docker-Build aus
   (Pfad-Disziplin/Ask-Gates; Build übernimmt architect nach Merge). Statische Prüfung des
   Dockerfile zeigt keine Build-Blocker: Base-Image `python:3.12-slim` existiert,
   COPY-Quellen (`requirements.txt`, `pyproject.toml`, `src/`) vorhanden, `useradd` in
   Debian-slim verfügbar, CMD-Modulpfad korrekt. Das Story-Akzeptanzkriterium
   „docker build erfolgreich + SMOKE (`GET /` → 200)" bleibt als architect-seitige
   Restprüfung nach Merge dokumentiert.

## Beobachtungen (keine FAIL-Gründe)

1. **TestClient-Deprecation-Warning** (`StarletteDeprecationWarning: httpx with
   starlette.testclient is deprecated`) — extern (fastapi/starlette), nicht von diesem Branch
   verursacht, bereits in 02-01 vorhanden. Kein Handlungsbedarf in dieser Story.
2. **Private Board-Attribute im Test** (`board._posts.maxlen`, `board._max_text_length`,
   `# noqa: SLF001`): `PostBoard` bietet keinen öffentlichen Limit-Getter. Die Tests prüfen
   zusätzlich verhaltensbasiert (FIFO greift bei 3001 Adds, `ValueError` bei 100001 Zeichen)
   — die Kernaussage hängt damit nicht am Privatzugriff. Akzeptabel.
3. **Dockerfile-Feinheiten:** (a) `RUN useradd` liegt nach `COPY src/` — der Layer wird bei
   jeder Code-Änderung neu ausgeführt (Millisekunden, wenige KB; optimaler: useradd vor
   COPY src). (b) `pyproject.toml` wird mitkopiert, von `pip install -r` nicht benötigt
   (~200 Bytes, kein eigener Layer). Beides kosmetisch.
4. **PyYAML-Quirk:** `on:` parst unter PyYAML (YAML 1.1) als Key `True` — bekanntes
   False-Positive; GitHub Actions interpretiert `on` korrekt. Trigger-, Job- und
   Step-Struktur vollständig validiert. Bare `push:`/`pull_request:` = alle Branches, valid.
5. **Dev-Dependencies im Image:** `requirements.txt` (nicht Teil dieser Story, von CI
   benötigt) enthält pytest/ruff/httpx und schifft sie damit ins Image. Abhilfe
   (requirements-dev.txt oder Multi-Stage-Build) wäre eine eigene Story — hier out of scope.
6. **Red-Phase dokumentiert:** Commit-Body enthält
   `red: ModuleNotFoundError src.adapters.main` — Umsetzung der Empfehlung aus Review 01-01.
   Historisch nicht reproduzierbar, aber plausibel-konsistent (Modul existierte vor dem
   Commit nicht, Collection-Error zwingend).
7. **mypy:** nicht Teil der Repo-Toolchain (keine Config, nicht in requirements) — für
   dieses Gate nicht prüfbar/nicht relevant; QA-Katalog dieser Story fordert nur pytest + ruff.

## Verifikations-Logs (Summary)

```
$ git branch --show-current
feature/03-01-docker-ci

$ pytest
tests/test_board.py .................... [ 45%]
tests/test_http_adapter.py ................ [ 81%]
tests/test_main_launcher.py ....... [ 97%]
tests/test_version.py . [100%]
44 passed, 1 warning in 0.72s
(20 + 16 + 7 + 1 = 44 — Erwartung 37 bestehende + 7 neue Launcher-Tests erfüllt)

$ ruff check .
All checks passed!

$ python3 -c "import yaml; yaml.safe_load(open('.github/workflows/ci.yml')); ..."
.github/workflows/ci.yml => OK
  {'name': 'CI', 'on'(=True): {'push': None, 'pull_request': None},
   'jobs': {'lint-test': {'runs-on': 'ubuntu-latest', steps: checkout@v4,
     setup-python@v5 (3.12), pip install -r requirements.txt, ruff check ., pytest -q},
   'docker-build': {'runs-on': 'ubuntu-latest', steps: checkout@v4, docker build .}}}
docker-compose.yml => OK
  {'services': {'netclip': {'build': '.', 'ports': ['8000:8000'],
   'environment': {'PORT': '8000', 'MAX_POSTS': '3000', 'MAX_TEXT_LENGTH': '100000'},
   'restart': 'unless-stopped'}}}

$ grep -rn "uvicorn" tests/            # Quell-Code, __pycache__ irrelevant
tests/test_main_launcher.py:4:  Docstring „Kein echter uvicorn-Start, kein Netz" — 0 Code-Treffer

$ git diff $(git merge-base main HEAD)..HEAD --stat
7 files changed, 252 insertions(+), 3 deletions(-)
(.dockerignore, .github/workflows/ci.yml, Dockerfile, README.md,
 docker-compose.yml, src/adapters/main.py, tests/test_main_launcher.py — exakt die Targets)

$ git diff $(git merge-base main HEAD)..HEAD --name-only -- src/core/ src/adapters/http.py src/web/ tests/test_board.py tests/test_http_adapter.py tests/fakes/
(leer — 0 geänderte Bestandsdateien)

$ git log -1 --format=%B
feat(03-01): docker + github actions ci
symbols: build_app, main | breaks: none | affects: <7 Target-Dateien> | tests: pytest 44 passed
red: ModuleNotFoundError src.adapters.main (Collection-Error vor Implementierung …)

$ git merge-tree --write-tree main HEAD
merge konfliktfrei

$ docker build — von QA bewusst NICHT ausgeführt (Ask-Gate; architect nach Merge)
```

## Urteil

**PASS.** Alle QA-seitig prüfbaren Akzeptanzkriterien sind erfüllt; die 7 Developer Targets
sind exakt umgesetzt (nichts mehr, nichts weniger). Restprüfung nach Merge beim architect:
`docker build .` + SMOKE (`GET /` antwortet mit 200). Merge nach `main` freigegeben
(nach User-Go).
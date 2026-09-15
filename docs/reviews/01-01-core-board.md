# QA-Review — Story 01-01-core-board

- **Datum:** 2026-09-15
- **QA-Manager:** QA-Gatekeeper
- **Branch:** `feature/01-01-core-board` (Commit `195e3bc`, Merge-Base `0b8628e`)
- **Urteil:** ✅ **PASS** — Freigabe für Merge nach `main` (Merge durch architect nach User-Go)

## Geprüfte Punkte

| Prüfpunkt | Ergebnis |
|-----------|----------|
| `pytest -q` grün (alle Board-Tests) | ✅ `21 passed in 0.07s` |
| `ruff check .` ohne Fehler | ✅ `All checks passed!` |
| `src/core/board.py` Import-Block: keine fastapi/http/uvicorn/socket/requests-Imports | ✅ nur stdlib: `__future__`, `collections.deque`, `datetime` (grep: 0 Treffer) |
| `PostBoard`-API exakt nach Design §1 (Signatures, Defaults 3000/100_000) | ✅ verifiziert gegen Design-Vorgaben |
| Post-Dict: `{id, text, timestamp ISO-8601-UTC, sender}` | ✅ inkl. tz-aware-UTC-Test (`utcoffset()==0`) |
| Validierung: leer/whitespace/zu lang → `ValueError`, deutsche Meldung mit Grenzwert | ✅ Meldung enthält `100000` (Default) bzw. `10` (custom); Grenzwert selbst erlaubt |
| `get_posts` komplett / `since_id=1` → ab ID 2 / `since_id=0` → alle, aufsteigend | ✅ je eigener Test |
| Clear all: Liste leer, `consume_cleared()` erst `True`, dann `False` (auch `False` vor Clear) | ✅ |
| Clear last: nur letzter Post weg, Signal gesetzt (auch auf leerem Board) | ✅ |
| FIFO: `max_posts=3`, 5 Adds → nur IDs 3,4,5 (deque maxlen) | ✅ |
| ID-Counter monoton (auch nach `clear_all` kein Neustart) | ✅ `test_..._id_monoton`: neue ID = 2 |
| `simuliere_post()` ohne Argumente deterministisch (Default 2026-01-01T12:00 UTC) | ✅ Test matcht exakt `DEFAULT_START.isoformat()` |
| REQ-002 (Post erscheint in Liste) | ✅ Add- + get_posts-Tests |
| REQ-004 (Sendezeit + Absender-IP) | ✅ timestamp ISO-UTC-String + sender-Tests |
| REQ-005 (Clear all) | ✅ `test_clear_all_leert_liste_und_consume_cleared_true_dann_false` |
| REQ-006 (Clear last) | ✅ 2 Tests (normal + leeres Board) |
| REQ-007 (RAM-only, Restart = leer) | ✅ `test_neues_board_ist_leer_ram_only` |
| REQ-010 (FIFO-Limit, `max_posts` konfigurierbar per Konstruktor) | ✅ `test_fifo_max_posts_3_mit_5_adds_nur_ids_3_4_5` (ENV-Wiring ist Adapter-Scope, Design §6) |
| REQ-011 (max. 100k Zeichen, Überschreiten → Fehler mit Hinweis) | ✅ 3 Tests inkl. Grenzwert-in-Meldung und exakt-am-Limit |
| Developer Targets: nur `src/core/board.py`, `tests/fakes/fake_clock.py`, `tests/test_board.py` | ✅ Commit `195e3bc` + `git diff $(git merge-base main feature)..feature --stat`: exakt 3 Dateien, 398 Insertionen (s. Beobachtung 1) |
| FakeClock vorhanden, genutzt, deterministisch | ✅ `FakeClock` (start `2026-01-01T12:00Z`, `tick()`), in ~20/21 Tests im Einsatz |
| Kein `datetime.now()` im Test-Pfad | ✅ grep: 0 Code-Treffer (nur Docstring-Erwähnung in fake_clock.py:3); Core nutzt feste Konstante `DEFAULT_SIMULATION_TIME` |
| Tests ohne FastAPI/Server/Netz lauffähig (NFR-002) | ✅ keine FastAPI-Imports in tests/, pytest lief offline |
| Tests-zuerst: Tests rot ohne Implementierung | ✅ QA-Simulation: `board.py` entfernt → `ModuleNotFoundError: No module named 'src.core.board'` (ImportError) — Red-Phase objektiv nachvollziehbar |
| Commit-Message: `feat(01-01): core postboard + fakeclock` | ✅ Konvention eingehalten |
| Commit-Body: `symbols: … \| breaks: … \| affects: … \| tests: …` | ✅ `symbols: PostBoard, FakeClock \| breaks: none \| affects: <3 Dateien> \| tests: pytest 21 passed` |
| Branch-Hygiene: 1 Commit auf Merge-Base, kein Story-Mix, sauberes Workdir | ✅ |

## Beobachtungen (keine FAIL-Gründe)

1. **`git diff main..feature --stat` zeigt 6 Dateien** — irreführend: `main` hat nach dem Branch-Fork
   Hygiene-Commit `bcbd0d8 chore(00-03): posix newlines am dateiende` erhalten (Dateienden in
   `requirements.txt`, `src/version.py`, `tests/test_version.py`). Der Feature-Branch hat diese
   Dateien **nicht angefasst** — nachgewiesen via `git diff $(git merge-base …)..feature --stat`
   (exakt 3 Dateien) und Commit-Inhalt. `git merge-tree`: Merge konfliktfrei.
2. **Red-Phase nur simulativ, nicht historisch belegt:** Alle 3 Dateien kamen in einem Commit.
   Git-Historie allein kann die Reihenfolge nicht zeigen; explizite Red-Phase-Notiz fehlt im
   Commit-Body. QA-Simulation (ImportError ohne `board.py`) bestätigt die Tests-zuerst-Disziplin
   inhaltlich. Empfehlung für Folge-Stories: Red-Ergebnis im Commit-Body dokumentieren
   (z.B. `red: ModuleNotFoundError` vor `green: pytest N passed`).
3. **`simuliere_post` nutzt eigene Konstante** `DEFAULT_SIMULATION_TIME` statt Import aus
   `tests/fakes/` — architektonisch korrekt (`src/` darf nicht von `tests/` importieren);
   der Test gleicht die Konstante mit `FakeClock.DEFAULT_START` ab. Kein Konflikt mit der Story.
4. **try/except statt `pytest.raises`** in den Validierungs-Tests — funktional äquivalent,
   ruff-konform; stilistischer Hinweis, kein Handlungsbedarf.

## Verifikations-Logs (Summary)

```
$ git branch --show-current
feature/01-01-core-board

$ pytest -q
21 passed in 0.07s

$ ruff check .
All checks passed!

$ grep -nE "fastapi|http|uvicorn|socket|requests" src/core/board.py
(keine Treffer)

$ grep -n "datetime.now" tests/test_board.py tests/fakes/fake_clock.py src/core/board.py
tests/fakes/fake_clock.py:3:  (Docstring, kein Code)

$ git diff main..feature/01-01-core-board --stat
6 files changed, 401 insertions(+), 3 deletions(-)   → 3 branch-eigene + 3 main-Skew (s. Beobachtung 1)

$ git diff $(git merge-base main feature/01-01-core-board)..feature/01-01-core-board --stat
3 files changed, 398 insertions(+)   (board.py, fake_clock.py, test_board.py — exakt die Targets)

$ git log -1 --format=%B feature/01-01-core-board
feat(01-01): core postboard + fakeclock
symbols: PostBoard, FakeClock | breaks: none | affects: src/core/board.py, tests/fakes/fake_clock.py, tests/test_board.py | tests: pytest 21 passed

$ Red-Phase-Simulation (Kopie in /tmp, board.py entfernt)
ModuleNotFoundError: No module named 'src.core.board'  → Tests rot ohne Implementierung ✓

$ git merge-tree --write-tree main feature/01-01-core-board
merge konfliktfrei
```
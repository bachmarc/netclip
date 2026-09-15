# QA-Review — Story 02-01-http-api

- **Datum:** 2026-09-15
- **QA-Manager:** QA-Gatekeeper
- **Branch:** `feature/02-01-http-api` (Commit `b3e96f6`, Merge-Base `e618327`)
- **Urteil:** ❌ **FAIL (Loop 1/3)** — zurück an Developer auf demselben Branch; siehe Fix-Aufträge

## Geprüfte Punkte

| Prüfpunkt | Ergebnis |
|-----------|----------|
| `pytest -q` grün (Board + Version + Adapter-Tests, Erwartung 33) | ✅ `33 passed, 1 warning in 0.52s` (20 board + 1 version + 12 adapter) |
| `ruff check .` ohne Fehler | ✅ `All checks passed!` |
| `git branch --show-current` | ✅ `feature/02-01-http-api` |
| Developer Targets — Diff nur `src/adapters/http.py` + `tests/test_http_adapter.py` | ✅ Merge-Base-Diff: exakt 2 Dateien, 269 Insertionen, keine weiteren |
| `src/core/board.py` unverändert | ✅ `git diff $(merge-base)..HEAD -- src/core/` → 0 Zeilen |
| Architektur-Trennung: Adapter importiert fastapi, delegiert an Core | ✅ alle Entscheidungen (Validierung, Clear, Cursor) im Core |
| Adapter dünn: keine add_post-Validierungs-Duplikate | ✅ kein `strip()`/`len()`/`max_text_length` in `http.py`; Validierung nur in `board.py:29-34` |
| Routen-Zeilenbudget 3-10 (Extraktion → Delegation → Antwort) | ✅ get_posts 4, add_post 8, clear 9, root 7 logische Zeilen |
| Fehlerformat: 400er liefern `{"error": ...}` | ✅ für alle **implementierten** 400er via Exception-Handler (`{"detail"}` wird zu `{"error"}` gemappt) |
| GET /api/posts → `{"posts": [...], "cleared": bool}` | ✅ inkl. `consume_cleared()` genau einmal (manuell verifiziert) |
| POST /api/posts: leer/zu lang → 400 `{"error": <deutsche Meldung>}` | ✅ manuell: Leertext → 400 `{'error': 'Text darf nicht leer sein.'}`; >Limit → 400 mit Grenzwert |
| POST /api/clear: mode=all/last → `{"cleared": true}`; mode=bogus/fehlt → 400 | ✅ manuell: `{'error': "mode muss 'all' oder 'last' sein."}` |
| GET / → 200 HTML; Platzhalter solange `src/web/index.html` fehlt | ✅ `src/web/` existiert nicht → Platzhalter „NetClip – Frontend folgt" |
| Client-IP als sender via `request.client.host` | ✅ `sender="testclient"` (TestClient-Standard-IP) |
| Injektion: `board`/`now_fn` + `app.state.board` | ✅ beides getestet (Timestamp exakt `2026-01-01T12:00+00:00`, Live-Wirksamkeit) |
| Kein Netzwerk im Test-Pfad: kein `uvicorn` in tests/ | ✅ `grep -rn "uvicorn" tests/` → 0 Treffer; nur `TestClient` |
| **POST /api/posts + /api/clear: ungültiger Body → HTTP 400 (Design §1 Z.45, Story Z.24-27)** | ❌ **500er-Crash** — siehe FAIL-Gründe |
| Commit-Message `feat(02-01): ...` + Body symbols/breaks/affects/tests | ✅ inkl. Red-Phase-Doku `red: ModuleNotFoundError src.adapters.http` (Umsetzung der 01-01-Empfehlung) |
| Git-Hygiene: 1 Commit auf Merge-Base, kein Story-Mix, kein main-Skew | ✅ `HEAD..main` leer; `git merge-tree`: konfliktfrei |

## FAIL-Grund: Ungültige Bodies → 500 statt 400 (Design §1, Story Z.24-27)

Design §1 (Z.45): *„Mapping: ValueError → HTTP 400 mit Meldung; **ungültiger Body**/Mode → HTTP 400."*
Story Z.26-27: *„POST /api/clear — Body `{"mode": "all"|"last"}`; ungültiger mode/**Body** → HTTP 400."*

Der Adapter extrahiert per `(await request.json()).get(...)` ohne Absicherung. Malformed JSON wirft
ungefilterte `JSONDecodeError`, fehlender `text`-Key liefert `None`, das den Core-Contract
(`text: str`) bricht und in `board.py:29` mit `AttributeError` crasht. In Produktion (uvicorn)
ergibt das 500er statt sauberer 400er.

Reproduktion (TestClient, `raise_server_exceptions=False` simuliert uvicorn-Verhalten):

| Request | IST | SOLL |
|---------|-----|------|
| `POST /api/posts` Body `{}` (text fehlt) | **500** (`AttributeError: 'NoneType' object has no attribute 'strip'`) | 400 `{"error": ...}` |
| `POST /api/posts` Body `{"text": 123}` (non-str) | **500** (`AttributeError: 'int' object has no attribute 'strip'`) | 400 `{"error": ...}` |
| `POST /api/posts` Body `kein json` (malformed) | **500** (`JSONDecodeError`) | 400 `{"error": ...}` |
| `POST /api/clear` Body `kein json` (malformed) | **500** (`JSONDecodeError`) | 400 `{"error": ...}` |

Nicht betroffen (falsch wäre Verallgemeinerung): Leertext, zu langer Text, `mode=bogus`,
fehlender `mode`-Key (`{}`) — all diese Fälle sind korrekt 400.

## Fix-Aufträge an Developer (Loop 1, Branch `feature/02-01-http-api`)

1. **`src/adapters/http.py:63` (Route `add_post`) — Body-Extraktion absichern:**
   - `await request.json()` in try/except nehmen → `JSONDecodeError` → `HTTPException(400, ...)`.
   - Nach Extraktion: `if not isinstance(text, str): raise HTTPException(400, ...)`
     (deutsche Meldung, z. B. „Body muss {\"text\": str} enthalten.").
   - **Inhaltliche Validierung (leer/zu lang) bleibt allein im Core** — kein Duplikat im Adapter
     (Typprüfung des Body-Schemas ist Adapter-Arbeit, da der Core-Contract `text: str` ist).
   - Alternative (ebenfalls dünn/ok): Pydantic-Model `text: str` + zusätzlicher
     `RequestValidationError`-Handler, der auf 400 + `{"error": ...}` mappt (nicht 422/`detail`).
2. **`src/adapters/http.py:72` (Route `clear`) — gleiche Absicherung** für `await request.json()`
   → `JSONDecodeError` → 400 `{"error": ...}`. (Fehlender `mode`-Key ist bereits korrekt: `None`
   → else-Zweig → 400.)
3. **`tests/test_http_adapter.py` — Test-first ergänzen** (vor Fix rot, danach grün):
   - `POST /api/posts` malformed JSON → 400 + `error`-Key
   - `POST /api/posts` `{}` (text fehlt) → 400 + `error`-Key
   - `POST /api/posts` `{"text": 123}` → 400 + `error`-Key
   - `POST /api/clear` malformed JSON → 400 + `error`-Key
   - Hinweis: Nach dem Fix wirft die Route keine rohen Exceptions mehr → normaler `TestClient`
     genügt (kein `raise_server_exceptions=False` nötig).
4. Commit wie gehabt: `fix(02-01): ...` + Body (`symbols/breaks/affects/tests`, gerne wieder `red:`-Zeile).

## Bewertung der gemeldeten Abweichungen

| Abweichung | Bewertung |
|------------|-----------|
| Zusätzlicher Test „fehlender mode → 400" | ✅ **Legitim** — direkte Konkretisierung von Story Z.26-27 („ungültiger mode/Body → 400"); `{}` ist der minimale ungültige Body. Innerhalb der Story-Abdeckung. |
| Zusätzlicher Platzhalter-Test („NetClip – Frontend folgt") | ✅ **Legitim** — Story Z.21-22 fordert den Platzhalter explizit; der Guard (Test überspringt sich, sobald `src/web/index.html` existiert) ist pragmatisch für 02-02-Parallelarbeit. Story-Target, kein Scope-Creep. |
| Zentraler `HTTPException`-Exception-Handler statt Inline-Mapping | ✅ **Legitim** — design-konform (§5-Fehlerformat `{"error"}`), DRY (ein Mapping statt pro Route), dünn (6 Zeilen), zukunftssicher für Folge-Stories. Kein Scope-Creep. **Aber:** Handler deckt nur `HTTPException` ab — `JSONDecodeError`/Contract-Brüche laufen ungefiltert durch. Genau das ist die FAIL-Ursache; der Handler selbst ist korrekt gebaut, die Extraktion davor fehlt die Absicherung. |

## Beobachtungen (keine FAIL-Gründe)

1. **FastAPI-Defaults außerhalb Story-Scope:** `GET /api/posts?since_id=abc` → 422
   `{"detail": [...]}` (Query-Typprüfung durch FastAPI) und `GET /nichtda` → 404
   `{"detail": "Not Found"}`. Weder Story noch Design §4 definieren Fehlerformate für Query-/
   Routing-Fehler — kein Handlungsbedarf in 02-01. Ggf. für Story 03-01 (CI/Deployment)
   im Blick behalten, falls ein einheitliches Fehlerformat gewünscht wird.
2. **Red-Phase-Doku im Commit-Body** (`red: ModuleNotFoundError src.adapters.http`) —
   Umsetzung der 01-01-Empfehlung; QA-Präferenz erfüllt. Weiter so.
3. **Kein main-Skew:** `main` hat seit Branch-Fork keine neuen Commits
   (`git log HEAD..main` leer) — Merge-Base-Diff ist hier identisch mit `main..HEAD`;
   Merge via `git merge-tree` konfliktfrei.
4. **pytest-Warnung** (`StarletteDeprecationWarning: httpx/starlette.testclient`) —
   Umweltbedingt (installierte httpx-Version), nicht branch-verursacht; Core-Tests
   (01-01) zeigen die Warnung nicht.

## Verifikations-Logs (Summary)

```
$ git branch --show-current
feature/02-01-http-api

$ pytest -q
33 passed, 1 warning in 0.52s

$ ruff check .
All checks passed!

$ git diff $(git merge-base main HEAD)..HEAD --stat
 src/adapters/http.py       |  83 ++++++++++++++++++++
 tests/test_http_adapter.py | 186 +++++++++++++++++++++++++++++++++++++
 2 files changed, 269 insertions(+)

$ git diff $(git merge-base main HEAD)..HEAD -- src/core/ | wc -l
0

$ grep -rn "uvicorn" tests/
(keine Treffer, Exit 1)

$ git log -1 --format=%B
feat(02-01): fastapi adapter (http-api)
symbols: create_app | breaks: none | affects: src/adapters/http.py, tests/test_http_adapter.py | tests: pytest 33 passed | red: ModuleNotFoundError src.adapters.http

$ git merge-tree --write-tree main HEAD
merge konfliktfrei

# Manuelle API-Prüfung (TestClient):
LEERTEXT:     400 {'error': 'Text darf nicht leer sein.'}          ✓
MODE_BOGUS:   400 {'error': "mode muss 'all' oder 'last' sein."}   ✓
CLEAR_ALL:    200 {'cleared': True}                                ✓
GET_POSTS:    200 {'posts': [], 'cleared': True} (genau einmal)    ✓
TEXT_INT:     500 (AttributeError)                                 ✗ SOLL 400
FEHLENDER_TEXT_KEY: 500 (AttributeError 'NoneType'.strip)          ✗ SOLL 400
MALFORMED_JSON:    500 (JSONDecodeError, beide Routen)             ✗ SOLL 400
```

## Nächster Schritt

Developer fixt auf `feature/02-01-http-api` (Fix-Aufträge 1-3), QA prüft erneut
(Loop 2 von max. 3). PASS erst wenn alle ungültigen Bodies sauber 400 + `{"error": ...}`
liefern und die neuen Tests grün sind.

## Loop 2 (2026-09-15) — Re-Review nach Fix-Commit `e78caa8`

- **Urteil:** ✅ **PASS (Loop 2/3)** — Freigabe für Merge nach `main` (wartet auf User-Go)
- **Geprüfter Stand:** Commit `e78caa8` „fix(02-01): ungueltige bodies -> 400 statt 500"

### Fix-Auftrags-Verifikation (alle 4 erfüllt)

| # | Fix-Auftrag (Loop 1) | Ergebnis | Verifikation |
|---|----------------------|----------|--------------|
| 1 | `add_post`: JSONDecodeError → 400, isinstance-Prüfung `text: str`, keine inhaltliche Validierung im Adapter | ✅ | Manueller Spot-Check (TestClient): `{}` und `{"text": 123}` → 400 `{"error": 'Body muss {"text": str} enthalten.'}`; Adapter enthält kein `strip()`/`len()`/`max_text_length` (grep: 0 Treffer) — leer/zu lang weiterhin allein im Core (`board.py:29-34`) |
| 2 | `clear`: JSONDecodeError → 400 | ✅ | Manuell: malformed JSON → 400 `{"error": 'Ungültiges JSON im Body.'}` |
| 3 | 4 neue Tests (test-first, rot→grün) | ✅ | `tests/test_http_adapter.py`: 4 neue Body-Tests (malformed ×2, `{}`, `{"text": 123}`), alle grün; normaler `TestClient` ohne `raise_server_exceptions=False` (wie empfohlen) |
| 4 | Commit-Konvention inkl. `red:`-Zeile | ✅ | Body: `symbols: create_app | breaks: none | affects: ... | tests: pytest 37 passed | red: 4 neue Tests schlugen fehl (500er)` — Red-Phase plausibel (4 Tests ↔ 4 Loop-1-Reproduktionen ↔ 500er-Verhalten des Loop-1-Stands) |

### Spot-Check-Outputs (TestClient, echte Requests)

```
POST /api/posts malformed:      400 {'error': 'Ungültiges JSON im Body.'}       OK
POST /api/posts {}:             400 {'error': 'Body muss {"text": str} ...'}    OK
POST /api/posts {"text": 123}:  400 {'error': 'Body muss {"text": str} ...'}    OK
POST /api/clear malformed:      400 {'error': 'Ungültiges JSON im Body.'}       OK
--- Regressionen (Loop-1-Positivfälle + Happy Path) ---
POST /api/posts leerer Text:    400 {'error': 'Text darf nicht leer sein.'}     OK
POST /api/posts zu lang (Limit injiziert): 400 {'error': 'Text ist zu lang ...'} OK
POST /api/clear mode=bogus:     400 {'error': "mode muss 'all' oder 'last' sein."} OK
POST /api/clear mode fehlt:     400 (dito)                                     OK
POST /api/posts happy / clear all|last / GET /api/posts / GET /:  alle 200      OK
ERGEBNIS: 13/13 OK
```

### Verifikations-Logs Loop 2

```
$ pytest -q
37 passed, 1 warning in 0.58s          # Erwartung 33 + 4 = 37 ✓ (Warnung umweltbedingt, s. Loop 1)

$ ruff check .
All checks passed!

$ git show e78caa8 --stat
 src/adapters/http.py       | 21 ++++++++++++++++--   # Diff-Hygiene: nur die 2 geforderten
 tests/test_http_adapter.py | 45 +++++++++++++++++++++++++++++-   # Dateien, kein Streu-Commit

$ git diff $(git merge-base main HEAD)..HEAD -- src/core/  →  leer  (Core unverändert ✓)

$ grep -rn "uvicorn" tests/ src/adapters/  →  0 Treffer
```

### Beobachtungen Loop 2 (keine FAIL-Gründe)

1. **main-Skew neu:** `main` hat seit Branch-Fork einen zusätzlichen Commit
   (`a73b673`, chore/Permissions — kein Code). `git merge-tree --write-tree main HEAD` →
   konfliktfrei, kein Handlungsbedarf.
2. **Kosmetik:** `tests/test_http_adapter.py` endet ohne Newline am Dateiende
   (vgl. `00-03` POSIX-Newline-Konvention). Kein Story-Kriterium, kein lint-Bruch —
   Hinweis für ggf. Aufräumen im nächsten Touch der Datei (nicht blockierend).
3. QP-Selbstkorrektur dokumentiert: Erster Spot-Check lief „zu lang → 200" — Ursache war
   ein QA-Skriptfehler (`create_app()`-Default-Limit 100 000 statt injiziertem Limit);
   mit `PostBoard(max_text_length=100)` injiziert korrekt 400. Kein Produktionsfehler.
4. Schema-Prüfung im Adapter ist bewusst minimal (`isinstance(body, dict)`,
   `isinstance(text, str)`): Non-Dict-Bodies (z. B. `[1,2]`) laufen sauber in den
   400-Zweig — konsistent mit Fix-Auftrag 1 („Typprüfung des Body-Schemas ist Adapter-Arbeit").
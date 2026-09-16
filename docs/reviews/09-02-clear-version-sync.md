# QA-Review — Story 09-02-clear-version-sync (REQ-019)

- **Datum:** 2026-09-16
- **Reviewer:** QA-Manager
- **Branch:** `feature/09-02-clear-version-sync` (Worktree `.worktrees/09-02-clear-version-sync`)
- **Loop:** 1/3
- **Basis:** `main` (Merge-Base `5c9018b`)
- **Commit:** `c195e7a` (`feat(09-02): clear-sync via version — alle Browser sehen jeden Clear`)

## Urteil: **PASS**

## Checkliste

| # | Prüfpunkt | Ergebnis | Nachweis |
|---|-----------|----------|----------|
| 1 | pytest grün (Erwartung: 74 − cleared-Tests + neue Version-Tests) | ✅ | `78 passed, 1 warning in 0.77s` — exakt +4 (74→78); Warning = bekannte Starlette/httpx-Deprecation, nicht story-relevant |
| 2 | ruff check . sauber | ✅ | `All checks passed!` |
| 3 | Requirements/Story-Targets erfüllt (REQ-019, Design §4/§4a) | ✅ | Siehe Traceability & Logik-Review unten — alle 8 Developer Targets umgesetzt, nicht mehr, nicht weniger |
| 4 | Architektur: core ohne HTTP/IO/Zeit, Adapter dünn | ✅ | `src/core/board.py` importiert nur stdlib (`collections`, `datetime`, `__future__`); `clear_version` als reine Property. `get_posts`-Route: 3 Zeilen Body, delegiert vollständig an Core |
| 5 | Fakes: kein Socket, kein Netz | ✅ | `fastapi.testclient.TestClient` (http.py-Header dokumentiert „kein Socket im Test-Pfad"), `FakeClock` in test_board.py; Laufzeit 0.77 s ohne Netzwerk |
| 6 | Git-Diff: nur betroffene Dateien | ✅ | 7 Dateien: `src/core/board.py`, `src/adapters/http.py`, `src/web/index.html`, 4× `tests/*` — alle laut Target-Liste; `src/adapters/main.py` unangetastet (Target: KEINE Änderung) |
| 7 | `consume_cleared` existiert nirgends mehr | ✅ | grep über `src/` + `tests/`: 0 Treffer. Nur historische Doku (Reviews/Stories 01-01, 02-01) verweist rückblickend — bewusst unverändert. `__pycache__`-Binär-Treffer sind ungetrackte Build-Artefakte |
| 8 | Contract-Fix `test_main_launcher.py` (cleared → clear_version) im Diff | ✅ | Exakt 1 Zeile geändert: `{"posts": [], "cleared": False}` → `{"posts": [], "clear_version": 0}` |

## Frontend-Logik-Review (`poll()` / `ladeAlles()`, Design §4a)

| Aspekt | Verhalten | Korrekt? |
|--------|-----------|----------|
| Initial-Load | `ladeAlles()` speichert `lastClearVersion = daten.clear_version` (mit `!== undefined`-Guard) | ✅ Target: „Initial-Load speichert Version" |
| Poll nach `clear_all` (2. Browser) | Versions-Abweichung → Version speichern → `listeLeeren()` (setzt `lastId = 0`) → `ladeAlles()` | ✅ Target: „Liste leeren, last_id = 0, neu rendern, Version aktualisieren" — vollständig |
| Poll nach `clear_last` | Gleiches Schema: Liste leeren + Full-Reload (statt diff) — zeigt korrigierte Liste statt gelöschtem Post | ✅ Konsistent mit Design §4a („neu laden") |
| Kein Post-Verlust beim Reload | `ladeAlles()` fragt ohne `since_id` (alles); Posts zwischen Clear und Reload werden erfasst | ✅ |
| Race eliminiert | Version konsumiert sich nicht — zweiter/dritter GET liefert gleiche Version (Adapter-Test pinnt: „kein consume-once") | ✅ Kernziel REQ-019 erfüllt |
| `POST /api/clear` → `{"cleared": True}` | Unverändertes statisches OK-Ack laut Design §3 API-Tabelle — NICHT das consume-once-Flag; JS wertet nur `antwort.ok` aus | ✅ Kein Verstoß, Target betraf nur GET /api/posts |

## Bewertung der dokumentierten Abweichung (Prüfpunkt 8)

**Contract-Fix in `tests/test_main_launcher.py`: GERECHTFERTIGT.**

- Die Story selbst autorisiert ihn explizit als Developer Target („ausschließlich 1-Zeilen-Contract-Fix erlaubt") inkl. QA-Vorab-Einordnung — damit ist er Teil des freigegebenen Plans, keine unangeforderte Änderung.
- Sachlich zwingend: Der Launcher-Test pinnt den API-Vertrag von `GET /api/posts`; da der Vertrag sich durch das Target selbst änderte (`cleared` → `clear_version`), wäre der unveränderte Test ein falscher Negativ-Pin des veralteten Vertrags.
- Minimal: exakt 1 Zeile, kein Verhaltens-Change im Launcher-Code. Der Test prüft weiterhin End-to-End (build_app → TestClient → `/api/posts`).

## Tests-zuerst (Red-Phase)

- Exakt **4 neue Version-Tests** (Story-Testkriterium „4 neue Version-Tests"): 2× test_board (`bleibt_bei_add_und_get_unveraendert`, `inkrementiert_bei_zweitem_clear`), 1× test_http_adapter (`initial_0`), 1× test_web_page (`polling_nutzt_clear_version`) — 74 + 4 = 78 bestätigt die Erwartung.
- Commit-Body dokumentiert Red-Phase: „red: 4 neue Version-Tests schlagen fehl (kein clear_version)" — statisch plausibel, da Vorgänger-Code kein `clear_version`-Attribut hatte.
- Adapter-Testkriterium erfüllt: „zweiter GET nach Clear liefert gleiche Version" — 2 Tests pinnen dies explizit.
- Testabdeckung laut Story vollständig: start 0, nach clear_all = 1, nach clear_last = 2, unverändert bei add/get.

## Traceability

`REQ-019` (Requirements: Clear-Sync für ALLE Clients via monotoner `clear_version`-Zähler) →
Design §4 (Clear-Signalisierung: Zähler, GET liefert Version, Clients vergleichen + neu laden) +
Design §3 API-Tabelle (`{"posts": [...], "clear_version": int}`) + §4a (Polling-Contract) →
Story 09-02 → Implementierung: `board.clear_version` (Property, Start 0, Inkrement je Clear),
`http.get_posts`, `index.html` (`lastClearVersion`-Vergleich), 78 Tests. Vollständig erfüllt.

## Git-Hygiene

- 1 fachlicher Commit `feat(09-02): ...` mit Metadaten-Body (`symbols/breaks/affects/tests` + Red-Phase) — Konvention eingehalten.
- `breaks: consume_cleared entfernt` korrekt deklariert (breaking für externe Consumer des alten Flags — im Repo-Scope vollständig migriert).
- Kein Mix mit anderen Stories; Working tree clean.

## Befunde

Keine Blocker, keine Rückbauten, keine unangeforderten Features, keine Architekturverstöße.

**INFO (kein Blocker):**
1. Nach Merge: STORIES.md/Story-Status „Geplant" → „Erledigt" nachziehen (separater docs-Commit, wie bei 08-01 üblich).
2. Historische Doku-Referenzen auf `consume_cleared` (stories/reviews 01-01, 02-01) bleiben bewusst unverändert (Historie).
3. `tests/test_board.py` / `tests/test_web_page.py` ohne trailing newline — bereits vor der Story so, ruff ohne W-Regeln; kosmetisch.

**Ergebnis: PASS — Freigabe für Merge nach `main` (nach explizitem User-Go, `--no-ff`).**
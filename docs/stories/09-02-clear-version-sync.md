# Story 09-02 — Clear-Sync: Version statt consume-once-Flag

Status: Erledigt (QA-PASS, Loop 1; User-Go)
Traceability: REQ-019 → Design §4 (Clear-Signalisierung), §4a (Frontend-Polling)

## Definition

`Clear all`/`Clear last` erreichten nur den ersten pollenden Browser (consume-once-Race).
Fix: Core-Zähler `clear_version` — alle Clients synchronisieren via Versionsvergleich.

## Entwicklungsziel

Jeder Clear wirkt für **alle** geöffneten Browser, auch für Tabs die gerade pausierten.

## Developer Targets (exakt, nicht mehr/nicht weniger)

- [ ] `src/core/board.py` — `consume_cleared()` entfernen, ersetzen durch:
  `clear_version: int` (Property/Counter, startet 0, inkrementiert je clear_all/clear_last)
- [ ] `src/adapters/http.py` — `GET /api/posts`: statt `cleared: board.consume_cleared()`
  liefert `{"posts": [...], "clear_version": board.clear_version}`
- [ ] `src/web/index.html` — Polling: statt `cleared: true`-Check vergleicht
  gespeichertes `lastClearVersion` mit `resp.clear_version`; bei Abweichung Liste leeren,
  `last_id = 0`, neu rendern, gespeicherte Version aktualisieren. Initial-Load speichert Version.
- [ ] `tests/test_board.py` — consume_cleared-Tests entfernen/ersetzen: Tests für
  `clear_version` (start 0, nach clear_all =1, nach clear_last =2, bleibt nach add/get unverändert)
- [ ] `tests/test_http_adapter.py` — `cleared`-Assertions ersetzen durch `clear_version`:
  GET liefert int, nach clear_all/clear_last inkrementiert (zweifacher GET nach Clear liefert gleiche Version, kein erneutes cleared:true)
- [ ] `tests/test_web_page.py` — Contract: `clear_version` im JS vorhanden, kein `consume_cleared`/`cleared`-Flag mehr
- [ ] KEINE Änderungen an: `src/adapters/main.py`
- [ ] `tests/test_main_launcher.py` — ausschließlich 1-Zeilen-Contract-Fix erlaubt
  (`cleared`-Assertion → `clear_version`), damit der End-to-End-Launcher-Test weiterhin den
  aktuellen API-Vertrag prüft. (Abweichung vom ursprünglichen „KEINE Änderung" — QA-seitig als
  gerechtfertigt eingeordnet, da Contract sich mit dem Target selbst geändert hat.)

## Akzeptanzkriterien (prüft QA-Manager)

- [ ] pytest grün (Erwartung: 74 bestehende - alte cleared-Tests + neue Version-Tests)
- [ ] ruff check . sauber
- [ ] Zweiter Browser nach Clear: pollt → sieht leere/korrigierte Liste (kein Race)
- [ ] Nur betroffene Dateien im Diff (core, http-adapter, web, tests)
- [ ] `consume_cleared` existiert nirgends mehr (grep)

## Testkriterien (müssen VOR Implementierung existieren)

- [ ] 4 neue Version-Tests laufen zuerst ROT (aktueller Code hat kein clear_version)
- [ ] Adapter-Tests: zweiter GET nach Clear liefert gleiche Version (nicht nur einmal)
- [ ] Frontend-Contract: `clear_version` statt `cleared` im JS
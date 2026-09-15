# QA-Review — Story 02-02-web-frontend

- **Datum:** 2026-09-15
- **QA-Manager:** QA-Gatekeeper
- **Branch:** `feature/02-02-web-frontend` (Commit `0538c87`, Merge-Base `d38c912`)
- **Urteil:** ✅ **PASS** — Freigabe für Merge nach `main` (Merge durch architect nach User-Go)
- **Loop:** 1/3

## Geprüfte Punkte

| Prüfpunkt | Ergebnis |
|-----------|----------|
| `pytest -q` grün (Erwartung 41 = 37 + 4 neue) | ✅ `41 passed, 1 warning in 0.59s` (21 board + 15 http + 1 version + 4 web) |
| `ruff check .` ohne Fehler | ✅ `All checks passed!` |
| UI-Texte deutsch (Senden, Clear all, Clear last, Fehlermeldungen) | ✅ `lang="de"`, Unterzeile deutsch; Fehlermeldungen deutsch („Netzwerkfehler beim Senden.", „Löschen fehlgeschlagen (…).", „Senden fehlgeschlagen (…)."); Server-Fehler („Text darf nicht leer sein.") via `daten.error` angezeigt. „Clear all"/„Clear last" wie per REQ-005/006 wörtlich gefordert |
| EINE HTML-Datei, kein Build-Step, keine externen CDN-Abhängigkeiten | ✅ grep `http://cdn\|https://\|http://\|script src=\|link href=\|<link\|src=` in index.html: **0 Treffer**; CSS im `<style>`, JS im `<script>` — 181 Zeilen, alles inline |
| Polling-Logik nach Design §4a — Initial `GET /api/posts` + `lastId=max(id)` | ✅ `ladeAlles()` beim Start (Z.114-128, 177), `lastId`-Update via `if (post.id > lastId)` (Z.107/123) |
| §4a — `setInterval` 2000 ms mit `since_id=lastId` | ✅ `POLL_MS = 2000`, `setInterval(poll, POLL_MS)` (Z.59/98/178) |
| §4a — `cleared: true` → Liste leeren, `lastId = 0`, sofort neu laden | ✅ `poll()`: `listeLeeren()` (leert Liste + `lastId = 0`) + `await ladeAlles()` (Z.100-104, 91-94) |
| §4a — neue Posts oben (prepend), `lastId` aktualisieren | ✅ `liste.prepend(li)` mit Kommentar „neueste oben" (Z.88) |
| §4a — Senden: POST → Feld leeren bei Erfolg + sofortiger Poll; 400 → Fehlermeldung, Text bleibt | ✅ `senden()` (Z.130-150): Erfolg → `eingabe.value = ""` + `await poll()`; `!antwort.ok` → `zeigeFehler(daten.error …)` + `return` (Text bleibt) |
| §4a — Clear-Buttons: `POST /api/clear {"mode": "all"\|"last"}` + sofortiger Poll | ✅ `clear(mode)` (Z.152-175), Listener auf `clear-all`/`clear-last` (Z.174-175) |
| §4a — `fetch` mit `async/await`, Fehler per `try/catch` (kurzer UI-Hinweis) | ✅ alle 4 Fetch-Funktionen async + try/catch → deutsche Meldung in `#status` (`role="alert"`), kein Crash |
| Zeitformat `DD.MM.YYYY HH:MM:SS` aus ISO-Timestamp | ✅ `zeigeZeit()` (Z.70-76): Regex auf ISO-`YYYY-MM-DDTHH:MM:SS` → `DD.MM.YYYY HH:MM:SS` |
| `white-space: pre-wrap` für Post-Text | ✅ `.text { white-space: pre-wrap; overflow-wrap: anywhere; }` (Z.39) |
| 02-01-Contract unverändert (`src/adapters/http.py` + `src/core/`) | ✅ `git diff $(git merge-base main HEAD)..HEAD -- src/adapters/ src/core/` → **0 Zeilen** |
| Developer Targets: nichts mehr/nichts weniger | ✅ Merge-Base-Diff: exakt `src/web/index.html` (+181) + `tests/test_web_page.py` (+45), 2 Dateien, 226 Insertionen |
| Testabdeckung — alle 4 geforderten Tests in `test_web_page.py` | ✅ (1) Datei existiert, (2) `GET /` 200 + `content-type` startswith `text/html`, (3) charakteristische Strings NetClip/Senden/Clear all/Clear last, (4) SMOKE-Contract `since_id`/`setInterval`/`/api/posts`/`/api/clear` |
| Tests ohne Browser/Netz (Testkriterien) | ✅ nur `TestClient` + `Path.read_text`, keine Browser-Engine, kein Socket |
| Tests-zuerst (Red-Phase-Doku im Commit-Body) | ✅ Commit-Body: „tests zuerst, gegen Platzhalter: 3 failed 1 passed" — **exakt plausibel** (Existenz ✗, Content-Type ✓ da Platzhalter auch text/html, UI-Strings ✗, Contract-Strings ✗); zusätzlich Docstring-Doku im Testfile; kein /tmp verwendet (Pfad-Disziplin) |
| Manuelle Funktionssimulation (TestClient + echte index.html) | ✅ 2× POST → 200; `GET /` liefert **byte-identisch** `src/web/index.html` (Vergleich `==` True); alle UI-Strings enthalten; API liefert beide Posts; 400-Pfad: `{"error": "Text darf nicht leer sein."}` deutsch — Adapter + Frontend greifen zusammen |
| Requirements-Traceability (REQ-002/003/004/005/006/009) | ✅ REQ-002 Textarea+Senden; REQ-003 initialer Vollabruf; REQ-004 Zeit+IP pro Post (`kopf`); REQ-005 Clear all; REQ-006 Clear last; REQ-009 2s-Polling live. (REQ-012 since_id als Bonus aus Design §4 abgedeckt) |
| Git-Hygiene | ✅ 1 Commit auf Merge-Base, kein Story-Mix, sauberes Workdir, `git merge-tree`: konfliktfrei, kein Main-Skew (`HEAD..main` leer) |
| Commit-Konvention | ✅ `feat(02-02): web-frontend (seite + polling)` + Body `symbols: none | breaks: none | affects: … | tests: pytest 41 passed` |

## Beobachtungen (keine FAIL-Gründe)

1. **Zeitanzeige ist UTC, keine lokale Zeitzone:** `zeigeZeit()` formatiert den ISO-8601-UTC-Timestamp
   (Design §1) ins deutsche Format, konvertiert aber nicht in lokale Zeit. Story/Design fordern nur das
   Format `DD.MM.YYYY HH:MM:SS` — Vorgabe eingehalten. Falls lokale Zeit gewünscht: neue Anforderung
   an architect/User (bewusst kein autonomes Feature ergänzt — Developer-Target-Disziplin ✓).
2. **Red-Phase-Doku folgt der Empfehlung aus Review 01-01 (Beobachtung 2):** Commit-Body dokumentiert
   `red: 3 failed 1 passed` vor `green: 41 passed` — nachvollziehbar und konsistent mit dem Platzhalter-
   Verhalten aus `http.py`. Prozess-Verbesserung wurde umgesetzt. 👍
3. **Defensive Doppel-Prüfung in `ladeAlles()`:** prüft selbst `cleared: true` — deckt die Race ab, dass
   zwischen `poll()` und Reload erneut gecleart wird. Innerhalb der §4a-Semantik (Signal wird konsumiert),
   keine Rekursionsgefahr.
4. **Mikrosekunden im Timestamp** werden vom Regex ignoriert (Anzeige auf Sekunden) — irrelevant für
   Anzeigeformat, Contract unberührt.

## Verifikations-Logs (Summary)

```
$ git branch --show-current
feature/02-02-web-frontend

$ git diff $(git merge-base main HEAD)..HEAD --stat
 src/web/index.html     | 181 +++++++++++++++++++++++++++++
 tests/test_web_page.py |  45 ++++++++
 2 files changed, 226 insertions(+)

$ git diff $(git merge-base main HEAD)..HEAD -- src/adapters/ src/core/ | wc -l
0

$ pytest -q
41 passed, 1 warning in 0.59s

$ pytest -q tests/test_board.py tests/test_http_adapter.py
36 passed  (21 + 15; +1 version +4 web = 41)

$ ruff check .
All checks passed!

$ grep -nE "http://cdn|https://|http://|script src=|link href=|<link|src=" src/web/index.html
(0 Treffer — keine externen Abhängigkeiten)

$ Funktionssimulation (TestClient + echte index.html, python3 stdin)
POST 1: 200 POST 2: 200
GET / status: 200 | content-type: text/html; charset=utf-8
GET / == Dateiinhalt src/web/index.html: True
alle UI-Strings (NetClip/Senden/Clear all/Clear last/Text einfügen): enthalten
GET /api/posts: ['QA-Sim Post 1', 'QA-Sim Post 2']
POST leerer Text: 400 {'error': 'Text darf nicht leer sein.'}

$ git log -1 --format=%B
feat(02-02): web-frontend (seite + polling)
symbols: none | breaks: none | affects: src/web/index.html, tests/test_web_page.py
| tests: pytest 41 passed | red: tests zuerst, gegen Platzhalter: 3 failed 1 passed

$ git merge-tree --write-tree main HEAD
merge konfliktfrei (kein Main-Skew)
```

## Ergebnis

**PASS** — alle Akzeptanzkriterien der Story erfüllt, Developer Targets exakt eingehalten,
02-01-Contract unberührt, Tests zuerst + grün, Architektur unangetastet (keine Core-/Adapter-Änderung).
Freigabe für Merge nach `main` per `git merge --no-ff feature/02-02-web-frontend` — nur nach User-Go.
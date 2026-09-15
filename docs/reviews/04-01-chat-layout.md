# QA-Review — Story 04-01-chat-layout

- **Datum:** 2026-09-15
- **QA-Manager:** QA-Gatekeeper
- **Branch:** `feature/04-01-chat-layout` (Commit `7e0728c`, Merge-Base `0b78fe3`) — Loop 1/3
- **Urteil:** ✅ **PASS** — Freigabe für Merge nach `main` (Merge durch architect nach User-Go)

## Geprüfte Punkte

| Prüfpunkt | Ergebnis |
|-----------|----------|
| `pytest -q` grün (48 bestehende + 3 neue Layout-Tests) | ✅ `51 passed, 1 warning in 0.61s` (Warning: pre-existing StarletteDeprecation) |
| `ruff check .` ohne Fehler | ✅ `All checks passed!` |
| REQ-013: Eingabebereich unten fixiert | ✅ `body` flex-column (`height: 100vh/100dvh`), `ul#liste` `order:1; flex:1; overflow-y:auto; min-height:0` (Scroll-Container), `#eingabebereich` `order:2; flex:0 0 auto; position:sticky; bottom:0` — bleibt bei Scrollen sichtbar (CSS Z.16-46) |
| REQ-013: neueste Posts ganz unten | ✅ `liste.appendChild(li)` (Z.123), API liefert aufsteigend; kein `prepend`/`insertBefore`/`insertAdjacentHTML` mehr (grep: 0 Treffer) |
| REQ-013: Liste scrollbar | ✅ `overflow-y: auto` auf `ul#liste` (Z.28) |
| Auto-Scroll-Regel: „am unteren Ende"-Erkennung VOR dem Anhängen | ✅ `warListeAmEnde()` (scrollHeight − scrollTop − clientHeight ≤ `SCROLL_TOLERANCE_PX = 30`) wird in `postAnzeigen()` **vor** `appendChild` aufgerufen (Z.113 vor Z.123), bedingtes `scrolleAnsEnde()` danach (Z.124-126) |
| Initial-Load scrollt ans Ende | ✅ `ladeAlles()` endet mit `scrolleAnsEnde()` (Z.163) |
| `cleared: true` → Liste leeren, `last_id = 0` (unverändert) | ✅ `poll()` Z.138-141 (`listeLeeren()` + `ladeAlles()`), `ladeAlles()` Z.156-157; `listeLeeren()` setzt `lastId = 0` (Z.129-132) — identisch zu 02-02 |
| 400-Fehler-Pfad intakt (Text bleibt, deutsche Meldung) | ✅ `senden()` Z.177-183: `!antwort.ok` → `zeigeFehler(daten.error …)` + `return` (Text bleibt); Erfolg → Feld leeren + sofortiger `poll()` (Z.184-185) |
| Polling unverändert (2 s, `since_id`, sofortiger Poll nach Aktionen) | ✅ `POLL_MS = 2000`, `setInterval(poll, POLL_MS)` (Z.82/217), `since_id=` + lastId (Z.136), sofortiger Poll nach Senden/Clear (Z.185/206) |
| Merge-Base-Diff: NUR `src/web/index.html` + `tests/test_web_page.py` | ✅ `git diff 0b78fe3..HEAD --stat`: exakt 2 Dateien, 131+/23−; Core/API/Adapter/bestehende Testdateien unangetastet (Developer Target „KEINE Änderungen an core/adapters/test_board/test_http_adapter/test_main_launcher" eingehalten) |
| UI-Texte deutsch, keine externen Abhängigkeiten | ✅ Strings „NetClip", „Senden", „Clear all", „Clear last", „Text einfügen …" etc. (7 Treffer); grep nach `http(s)://`, CDN, `script src`, `link`, `@import`: 0 Treffer — kein Framework, kein CDN |
| 4 Web-Tests aus 02-02 weiterhin erfüllt (Strings + Contract) | ✅ `test_web_index_html_existiert`, `test_get_root_liefert_200_und_text_html`, `test_get_root_liefert_charakteristische_ui_strings`, `test_web_index_html_enthaelt_polling_contract_strings` — alle PASSED; Strings `since_id`, `setInterval`, `/api/posts`, `/api/clear` unverändert |
| Tests-zuerst: Red-Phase gegen alte prepend-Implementierung | ✅ Commit-Body dokumentiert Red-Phase (`red: 3 neue Layout-Contract-Tests ROT …`) — Empfehlung aus Review 01-01 umgesetzt. QA-Simulation: Merge-Base-Version von `index.html` ausgecheckt → **exakt die 3 neuen Tests FAILED** (`3 failed, 4 passed`), neue Implementierung wiederhergestellt → `7 passed`. Red-Phase objektiv nachvollziehbar |
| 3 neue Tests plausibel & strikt | ✅ append-vs-prepend-Semantik, scrollTop/scrollHeight/clientHeight + Toleranz 30 + Reihenfolge `warAmEnde < append` (echte Index-Prüfung!), flex-direction/order/sticky/overflow-y — Contract-Tests decken alle Story-Targets ab |
| Commit-Message: `feat(04-01): …` + Metadaten-Body | ✅ `feat(04-01): chat-layout — chronologisch, eingabe unten, auto-scroll` + `symbols/breaks/affects/tests/red` |
| Branch-Hygiene: 1 Feature-Commit auf Merge-Base, kein Story-Mix, sauberes Workdir | ✅ `main..HEAD`: nur `7e0728c` (Replanning-Commit `0b78fe3` ist der Merge-Base selbst); `git status` clean |
| Architektur-Trennung | ✅ Kein `src/core`/`src/adapters`-Contact; reine Frontend-/Test-Änderung; kein IO/Framework-Import-Thema berührt |

## Verifikations-Logs (Summary)

```
$ git branch --show-current
feature/04-01-chat-layout

$ git log main..HEAD --oneline
7e0728c feat(04-01): chat-layout — chronologisch, eingabe unten, auto-scroll

$ git merge-base main HEAD
0b78fe3

$ git diff 0b78fe3..HEAD --stat
 src/web/index.html     | 81 +++++---
 tests/test_web_page.py | 73 ++++-
 2 files changed, 131 insertions(+), 23 deletions(-)

$ pytest -q
51 passed, 1 warning in 0.61s          (48 bestehende + 3 neue; Warning pre-existing Starlette)

$ ruff check .
All checks passed!

$ grep -nE 'https?://|cdn|unpkg|jsdelivr|<link|<script src|@import' src/web/index.html
(keine Treffer — keine externen Abhängigkeiten)

$ grep -nE 'liste\.prepend|insertBefore|insertAdjacentHTML' src/web/index.html
(keine Treffer — Chat-Semantik sauber)

$ Red-Phase-Simulation (git checkout 0b78fe3 -- src/web/index.html)
FAILED test_web_index_html_haengt_neue_posts_unten_an
FAILED test_web_index_html_automatisch_scrollen_am_unteren_ende
FAILED test_web_index_html_layout_eingabebereich_unten_fixiert
3 failed, 4 passed  → genau die 3 neuen Tests ROT gegen prepend-Implementierung ✓
(Restaurierung via git checkout HEAD -- …; Working Tree danach clean)

$ mypy src tests
INTERNAL ERROR (mypy 2.3.0) — identisch am Merge-Base reproduziert, also pre-existing
Werkzeug-Problem, kein Branch-Regressionsindikator; keine mypy-Konfiguration im Projekt
(Projekt-Gate ist pytest + ruff, s. Story 03-01 CI)
```

## Beobachtungen (keine FAIL-Gründe)

1. **Laxer Matcher im Auto-Scroll-Test:** `assert "ScrollTo" in content or "scrollTo" in content`
   matcht versehentlich als Substring von `scrollTop` — der Matcher prüft faktisch nur
   `scrollTop` doppelt. Keine Auswirkung hier (das reale Scroll-Verhalten steckt in
   `scrolleAnsEnde()` → `liste.scrollTop = liste.scrollHeight`, Z.96-98, und die übrigen
   Assertions der 3 Tests sind strikt, inkl. echter Reihenfolge-Prüfung
   `content.index("warAmEnde") < content.index("liste.append…")`).
   Empfehlung für künftige Contract-Tests: absichtsgleiche Matcher wählen
   (z.B. `"scrolleAnsEnde"` bzw. `"scrollTop = list"`).
2. **`#status` (Fehleranzeige) in `#eingabebereich` verschoben** (vorher separat zwischen
   Buttons und Liste). Nicht explizit vom Target gefordert, aber stimmige Layout-Entscheidung
   im Rahmen der geforderten Seitenumstrukturierung: Fehlermeldung direkt an der Eingabe,
   wo der Nutzer agiert. Kein unangefordertes Feature.
3. **`position: sticky; bottom: 0` ist neben `flex: 0 0 auto` redundant** (die Liste ist
   selbst der Scroll-Container, der Eingabebereich bleibt ohnehin sichtbar). Story verlangt
   ausdrücklich „CSS flex/sticky"-Matcher — beide erfüllt, robust über zwei Layout-Mechanismen.
4. **`height: 100dvh`-Fallback** (`100vh` davor) — korrektes Progressive Enhancement ohne
   Framework, mobile-safe. OK.
5. **No newline at end of file** in `tests/test_web_page.py` — pre-existing Muster
   (Merge-Base endete ebenso), ruff-Konfiguration beanstandet es nicht. Kosmetik.

## Urteil

Alle Developer Targets exakt erfüllt, REQ-013 vollständig abgedeckt (Eingabe unten fixiert,
neueste unten, scrollbar, Auto-Scroll-Regel mit End-Erkennung VOR dem Anhängen, Initial-Load
am Ende), Red-Phase objektiv belegt, 51 Tests grün, ruff sauber, Diff minimal (2 Dateien).
**PASS — Freigabe für Merge nach `main` nach User-Go.**
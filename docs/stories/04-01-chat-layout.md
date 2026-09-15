# Story 04-01 — Chat-Layout: chronologische Liste, Eingabe unten

Status: Geplant
Traceability: REQ-013 → Design §4a (Layout & Auto-Scroll-Regel)

## Definition

Frontend-Replanning gemäß User-Feedback: Neues wurde über Altes eingefügt (altes §4a-Design
„neueste oben"). Neues Chat-Layout: **Eingabebereich unten fixiert, Posts chronologisch
(neueste ganz unten), Liste scrollbar.** Reine Frontend-Änderung — Core/API unverändert
(liefern bereits aufsteigend).

## Entwicklungsziel

NetClip verhält sich wie ein Chat: neueste Nachricht unten, direkt über dem fixierten
Eingabefeld; ältere Posts per Scroll nach oben erreichbar.

## Developer Targets (exakt, nicht mehr/nicht weniger)

- [ ] `tests/test_web_page.py` — ERST erweitern (vor Implementierung, Red-Phase via git stash):
  - Neue Tests für Chat-Layout-Contract in `src/web/index.html` (Datei-Inhalt-Checks):
    - `appendChild` bzw. `append` für neue Posts vorhanden; `prepend`/`insertBefore`/`insertAdjacentHTML(afterbegin)` NICHT mehr für die Post-Liste verwendet (Chat-Semantik)
    - Auto-Scroll: `scrollTop`-/`scrollHeight`-Logik vorhanden (am unteren Ende) + „am unteren Ende"-Erkennung (z.B. Distanz-Toleranz vor `appendChild`)
    - Layout: CSS enthält fixierten/sticky/flexiblen Eingabebereich unten (Matcher z.B. `flex-direction: column`, `order` oder `position: sticky/fixed` für den Eingabebereich bzw. Container-Layout)
  - Bestehende 4 Tests müssen weiter grün bleiben (Strings „NetClip", „Senden", „Clear all", „Clear last", `since_id`, `setInterval`, `/api/posts`, `/api/clear` unverändert)
- [ ] `src/web/index.html` — anpassen:
  - **Layout:** Seitenstruktur = Scroll-Container (Post-Liste) oben + fixierter Eingabebereich (Textarea, „Senden", „Clear all", „Clear last") unten — Eingabebereich bleibt bei Scrollen sichtbar (CSS flex/sticky, kein iframe, kein externes Framework)
  - **Reihenfolge:** Posts chronologisch rendern — API liefert aufsteigend; neue Posts **unten anhängen** (`appendChild`/`append`)
  - **Auto-Scroll-Regel (Design §4a):** Neue Posts → ans untere Ende scrollen, ABER nur wenn Nutzer am unteren Ende war (Erkennung vor dem Anhängen; Toleranz ~30px sinnvoll). Initial-Load: ans untere Ende scrollen.
  - **Clear-Reset:** `cleared: true` → Liste leeren, `last_id=0` (unverändert)
  - Sonstiges Verhalten (Polling 2s, sofortiger Poll nach Aktionen, Fehleranzeige, Text bleibt bei 400) unverändert
- [ ] KEINE Änderungen an: `src/core/`, `src/adapters/`, `tests/test_board.py`, `tests/test_http_adapter.py`, `tests/test_main_launcher.py`

## Akzeptanzkriterien (prüft QA-Manager)

- [ ] pytest grün (Erwartung: 48 bestehende + neue Layout-Tests)
- [ ] `ruff check .` sauber
- [ ] `src/web/index.html`: Eingabebereich unten fixiert; neue Posts erscheinen unten; Auto-Scroll nur bei „am unteren Ende"-Position
- [ ] API/Core/Adapter-Dateien unverändert (Merge-Base-Diff zeigt nur index.html + test_web_page.py)
- [ ] UI-Texte weiterhin deutsch; keine externen Abhängigkeiten

## Testkriterien (müssen VOR Implementierung existieren)

- [ ] Neue Layout-Tests in `tests/test_web_page.py` laufen zuerst ROT (gegen die bisherige prepend-Implementierung), Red-Phase im Commit-Body dokumentiert
- [ ] Nur statische Contract-Checks + bestehende TestClient-Tests — kein Browser, kein Netz
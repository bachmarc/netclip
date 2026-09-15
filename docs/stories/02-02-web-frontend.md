# Story 02-02 — Frontend (Seite + Polling)

Status: Geplant
Traceability: REQ-002, REQ-003, REQ-004, REQ-005, REQ-006, REQ-009 → Design §4 (API-Skizze), §4a (Polling-Verhalten)

## Definition

Statische deutsche Single-Page `src/web/index.html` (pures HTML+JS, kein Build-Step, keine externen
CDN-Abhängigkeiten), entwickelt gegen den **eingefrorenen API-Contract aus Design §4**.

## Entwicklungsziel

Volle UI: Posten, Ansehen, Clear all/Clear last — mit 2s-Polling (Cursor-optimiert).

## Developer Targets (exakt, nicht mehr/nicht weniger)

- [ ] `src/web/index.html` — eine Datei, enthält HTML + CSS (im `<style>`) + JS (im `<script>`):
      - Überschrift „NetClip", Unterzeile mit Kurzerklärung (deutsch)
      - Textfeld (`<textarea>`) + Button „Senden"; Buttons „Clear all" und „Clear last"
      - Post-Liste: neuester Post oben; pro Post Zeile mit Zeit + IP (Absender) und Text
        (Zeit deutsches Format `DD.MM.YYYY HH:MM:SS`, Text `white-space: pre-wrap`)
      - Fehleranzeige aus 400-Antworten (`{"error": …}`) als kurze Meldung im UI
- [ ] JS-Logik exakt nach Design §4a:
      - Initial `GET /api/posts` → Liste rendern, `lastId = max(id)`
      - `setInterval` 2000 ms: `GET /api/posts?since_id=lastId`
      - `cleared: true` → Liste leeren, `lastId = 0`, sofort neu laden
      - Neue Posts oben einfügen, `lastId` aktualisieren
      - „Senden": `POST /api/posts` mit `{"text": …}` → Textfeld leeren bei Erfolg, sofortigen Poll;
        bei 400 → Fehlermeldung anzeigen, Text bleibt im Feld
      - „Clear all"/„Clear last": `POST /api/clear` mit `{"mode": "all"|"last"}` → sofortiger Poll
      - `fetch` mit `async/await`, Fehler per `try/catch` (kurzer UI-Hinweis, kein Crash)
- [ ] `tests/test_web_page.py` — Tests mit `TestClient`:
      - Datei `src/web/index.html` existiert
      - `GET /` liefert die Datei aus (Matcher auf charakteristische Strings:
        „NetClip", „Senden", „Clear all", „Clear last")
      - Statischer SMOKE-Test des JS: Datei-Inhalt enthält `since_id`, `setInterval`,
        `/api/posts`, `/api/clear` (Verifikation der Polling-/Contract-Anbindung)
      - `Content-Type` der `GET /`-Antwort ist `text/html`

## Akzeptanzkriterien (prüft QA-Manager)

- [ ] `pytest` grün (neue Tests + alle bisherigen)
- [ ] UI-Texte deutsch („Senden", „Clear all", „Clear last", Fehlermeldungen)
- [ ] Kein Build-Step, keine externen CDN-Abhängigkeiten — eine einzige HTML-Datei
- [ ] Polling-Logik folgt Design §4a (Cursor + Clear-Signal-Reset)
- [ ] 02-01-Routen unverändert (Contract eingehalten — kein Adapter-Umbau in dieser Story)
- [ ] `ruff check .` ohne Fehler

## Testkriterien (müssen VOR Implementierung existieren)

- [ ] `tests/test_web_page.py` läuft ohne Browser, ohne Netz (nur `TestClient` + Datei-Lesen)
- [ ] Contract-Strings als Tests definiert, bevor JS/HTML implementiert wird
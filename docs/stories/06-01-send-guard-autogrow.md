# Story 06-01 — Send-Guard + Auto-Grow-Textarea

Status: Geplant
Traceability: REQ-015, REQ-016 → Design §4a (Send-Guard, Auto-Grow-Textarea)

## Definition

Zwei UX-Fixes im Eingabebereich:
1. **Send-Guard:** „Senden" während des laufenden POST-Requests deaktiviert — Doppelklicks
   erzeugen keine doppelten Posts mehr.
2. **Auto-Grow:** Textarea wächst mit dem Text mit (ab dem Moment, wo der Text mehr Platz
   braucht), bis max. ~40vh; danach scrollt sie intern. Nach Senden/Leeren: Reset auf
   Ausgangshöhe.

Reine Frontend-Änderung — Core/API unberührt.

## Entwicklungsziel

Keine doppelten Nachrichten mehr; komfortables Tippen längerer Texte ohne Mini-Fenster.

## Developer Targets (exakt, nicht mehr/nicht weniger)

- [ ] `tests/test_web_page.py` — ERST erweitern (vor Implementierung, Red-Phase via git stash):
  - **Send-Guard-Contract:** `disabled`-Setzung im `senden()`-Pfad vorhanden (Button wird
    zu Beginn deaktiviert, im `finally`/nach Antwort wieder aktiviert) — Matcher: `disabled = true`
    (bzw. `disabled=true`) vor dem `await fetch`, Reaktivierung danach/finally
  - **Auto-Grow-Contract:** `input`-EventListener auf der Textarea vorhanden; Höhen-Anpassung
    `scrollHeight` + `max-height`-Begrenzung im CSS (z.B. `40vh`); Reset auf Ausgangshöhe
    nach erfolgreichem Senden (Matcher: Höhen-Reset im Senden-Erfolgs-Pfad oder via
    `style.height`-Reset-Funktion)
  - Bestehende Tests unverändert grün
- [ ] `src/web/index.html` — anpassen:
  - **Send-Guard:** `senden()` deaktiviert den Senden-Button vor dem `fetch`, reaktiviert
    ihn nach Abschluss (finally), Erfolgspfad unverändert (Textfeld leeren + Poll)
  - **Auto-Grow:** Textarea per `input`-Event auto-resize (`height:auto` →
    `height: scrollHeight px`, CSS `min-height` + `max-height: 40vh`); nach erfolgreichem
    Senden zurück auf Ausgangshöhe; Fehlerfall: Höhe bleibt (Text bleibt ja auch)
  - NICHTS anderes ändern (Polling, Auto-Scroll, Layout-Struktur, Clear-Buttons unverändert)
- [ ] KEINE Änderungen an: `src/core/`, `src/adapters/`, anderen Tests

## Akzeptanzkriterien (prüft QA-Manager)

- [ ] pytest grün (Erwartung: 52 bestehende + 2 neue Tests)
- [ ] `ruff check .` sauber
- [ ] Send-Guard: Button-Disable im Request-Pfad, Reaktivierung in jedem Fall (auch bei Fehler)
- [ ] Auto-Grow: wächst mit Text, Deckelung bei max-height, interner Scroll darüber, Reset nach Senden
- [ ] Nur `src/web/index.html` + `tests/test_web_page.py` im Diff
- [ ] UI weiterhin deutsch, keine externen Abhängigkeiten, keine Regressionen

## Testkriterien (müssen VOR Implementierung existieren)

- [ ] 2 neue Contract-Tests laufen zuerst ROT (aktuelles HTML hat weder Guard noch Auto-Grow)
- [ ] Statische Checks — kein Browser, kein Netz; echte Doppelklick-Verifikation bleibt manueller
  SMOKE nach Deploy (durch User)
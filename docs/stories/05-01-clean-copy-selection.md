# Story 05-01 — Copy-freundliche Text-Markierung (ohne Zeitstempel/IP)

Status: Geplant
Traceability: REQ-014 → Design §4a (Text-Markierung)

## Definition

Maus-Markierung über mehrere Posts hinweg soll NUR die Post-Texte erfassen —
Kopfzeilen (Zeitstempel + IP) werden bei der Auswahl übersprungen (`user-select: none`).
Ergebnis: Copy-Paste liefert fortlaufend die reinen Textinhalte.

## Entwicklungsziel

Texte aus mehreren Posts in einer Aktion markieren und kopieren, ohne Nachbearbeitung
(keine Zeitstempel/IP-Anteile in der Zwischenablage).

## Developer Targets (exakt, nicht mehr/nicht weniger)

- [ ] `tests/test_web_page.py` — ERST erweitern (vor Implementierung, Red-Phase via git stash):
  - Neuer Test: `src/web/index.html` enthält `user-select: none` (bzw. `user-select:none`)
    UND es ist der Kopfzeilen-Elementen/Selektor zugeordnet (Matcher: Vorkommen in CSS
    zusammen mit dem Kopfzeilen-Selektor der Post-Kopfzeile, z.B. `kopf`-Klasse — exakten
    Selektor aus der Implementierung ableiten, Test prüft Kombination)
  - Negativ-Check: Post-**text**-Elemente sind NICHT `user-select: none` (Text bleibt markierbar)
  - Bestehende Tests (7 Web-Tests inkl. Layout-Contract) unverändert grün
- [ ] `src/web/index.html` — anpassen:
  - CSS: `user-select: none` auf der Kopfzeile jedes Posts (Zeit + IP), NICHT auf dem Text
  - KEINE weiteren Änderungen (Layout, Polling, Auto-Scroll, Buttons unverändert)
- [ ] KEINE Änderungen an: `src/core/`, `src/adapters/`, anderen Tests

## Akzeptanzkriterien (prüft QA-Manager)

- [ ] pytest grün (Erwartung: 51 bestehende + 1 neuer Test)
- [ ] `ruff check .` sauber
- [ ] Kopfzeile (Zeit + IP) nicht markierbar, Post-Text markierbar (statische Contract-Prüfung)
- [ ] Nur `src/web/index.html` + `tests/test_web_page.py` im Diff
- [ ] Keine Regression im Layout/Polling (bestehende Web-Tests grün)

## Testkriterien (müssen VOR Implementierung existieren)

- [ ] Neuer Markierungs-Test läuft zuerst ROT (aktuelles HTML hat kein `user-select: none`)
- [ ] Statischer Contract-Check — kein Browser, kein Netz
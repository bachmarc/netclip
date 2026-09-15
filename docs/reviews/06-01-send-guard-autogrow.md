# QA-Review — Story 06-01: Send-Guard + Auto-Grow-Textarea

- **Datum:** 2026-09-15
- **QA-Loop:** 1/3
- **Branch:** `feature/06-01-send-guard-autogrow` (Worktree `.worktrees/06-01-send-guard-autogrow`)
- **Commits unter Review:** `29d0d0a` feat(06-01): send-guard + auto-grow-textarea
- **Traceability:** REQ-015, REQ-016 → Design §4a (Send-Guard, Auto-Grow-Textarea)

## Urteil: PASS ✅

Freigabe für Merge nach `main` (nur nach explizitem User-Go, `git merge --no-ff feature/06-01-send-guard-autogrow`).

## Checkliste

| # | Prüfpunkt | Ergebnis |
|---|-----------|----------|
| 1 | pytest grün (Erwartung 54 passed) | ✅ **54 passed** in 0.61s (52 bestehende + 2 neue) |
| 2 | `ruff check .` sauber | ✅ All checks passed |
| 3 | Send-Guard: Disable VOR fetch, Reaktivierung in finally | ✅ Manuell verifiziert (s. unten) |
| 4 | Auto-Grow: input-Listener + scrollHeight + max-height/overflow-y + Reset nur im Erfolgspfad | ✅ Manuell verifiziert (s. unten) |
| 5 | Nur 2 Dateien im Merge-Base-Diff | ✅ `src/web/index.html` (+20) + `tests/test_web_page.py` (+113/-1) |
| 6 | Keine Regressionen (sticky/append/Auto-Scroll, Polling, Clear, 52 Tests) | ✅ Diff rein additiv, alle bestehenden Tests grün |
| 7 | Tests-zuerst (Red-Phase dokumentiert + plausibel) | ✅ Commit-Body `red:`-Doku; statisch nachvollzogen |
| 8 | Architektur-Trennung | ✅ `src/core/` + `src/adapters/` unberührt, reine Frontend-Änderung |
| 9 | Git-Hygiene | ✅ feat(06-01)-Commit, Metadaten-Body, kein Story-Mix |
| 10 | UI deutsch, keine externen Abhängigkeiten | ✅ Kein CDN/import, alle Texte deutsch |

## Manuelle Code-Inspektion (src/web/index.html)

**Send-Guard (`senden()`, Zeilen 183–208):**
- Zeile 186: `sendenButton.disabled = true` steht **vor** dem `try`/`await fetch` (Zeile 188) —
  zwischen `zeigeFehler("")` und Disable läuft kein `await`, d.h. kein Event-Loop-Yield → kein
  Doppelklick-Fenster. Reihenfolge korrekt.
- Zeile 205–206: `finally { sendenButton.disabled = false; }` → Reaktivierung **in jedem Fall**.
- Edge-Fälle statisch geprüft:
  - **Netzwerkfehler** (fetch wirft): catch zeigt Fehler, finally reaktiviert Button; Höhe bleibt
    (Reset nur im try-Erfolgspfad). ✅
  - **400-Fehler** (leerer Text / zu lang): `!antwort.ok` → Fehlermeldung + `return` innerhalb
    try → finally läuft → Button reaktiviert; Text + Höhe bleiben. ✅
- `await poll()` liegt innerhalb des try → Button bleibt bis Poll-Abschluss konservativ disabled.
  Minimal länger gesperrt als nötig, aber korrekt und kein Kriterium verletzt.

**Auto-Grow (Zeilen 106–116, 234, CSS 47–56):**
- `passeEingabeHoeheAn()`: `style.height = "auto"` → `style.height = scrollHeight + "px"`
  (Muster exakt wie Design §4a). ✅
- CSS `#eingabe`: `min-height: 5rem` (Ausgangshöhe), **`max-height: 40vh`**, **`overflow-y: auto`**
  → Deckelung + interner Scroll über 40vh. ✅
- `eingabe.addEventListener("input", passeEingabeHoeheAn)` (Zeile 234). ✅
- `setzeEingabeHoeheZurueck()` setzt `style.height = "5rem"` (= CSS-min-height = Ausgangshöhe),
  **ausschließlich im Erfolgspfad** nach `eingabe.value = ""` (Zeile 201); catch/return-Pfade
  rufen ihn nicht → Fehlerfall: Höhe bleibt. ✅

## Tests-zuerst (Red-Phase)

- Commit-Body: `red: beide neuen Contract-Tests liefen zuerst rot (2 failed, 52 passed via git
  stash Baseline 52 passed)` ✅
- Statisch nachvollzogen: Alle 8 Matcher (disabled=true/false, finally, input-Listener,
  height-auto, scrollHeight, max-height 40vh, overflow-y) fehlen im merge-base-HTML →
  beide Tests wären gegen den alten Stand rot gelaufen. Plausibel und konsistent.
- Die 2 „Deletions" in `tests/test_web_page.py` betreffen nur die EOF-Newline-Umschreibung der
  letzten Zeile — bestehende Tests inhaltlich unverändert.

## Bewertung der gemeldeten Abweichungen

1. **Test-Matcher: direkter Reset ODER Reset-Funktion** — Story Zeile 29–30 erlaubte beide
   Varianten explizit („direkt … oder via style.height-Reset-Funktion"). Der Test prüft beide
   Pfade (if/else mit Funktionsauflösung). Kein Verstoß, exakt laut Target. **OK.**
2. **`resize: vertical` belassen** — Bestandteil des alten CSS, nicht neu hinzugefügt. Story
   verlangte „NICHTS anderes ändern" → Belassen war korrekt, kein Scope-Creep. Interaktion mit
   Auto-Grow unkritisch: ein input-Event überschreibt manuelle Größen ohnehin.
   **OK — Developer hat sich exakt an die Targets gehalten.**

## Anmerkungen (keine FAIL-Gründe)

- `tests/test_web_page.py` endet weiterhin ohne abschließenden Newline (war bereits so,
  ruff/pytest meckern nicht) — kosmetisch, bei Gelegenheit aufräumen.
- Echte Doppelklick-/Wachstums-Verifikation bleibt wie in der Story vorgesehen dem manuellen
  SMOKE nach Deploy überlassen (User).

## Ergebnis

**PASS — Loop 1/3.** Alle Akzeptanzkriterien erfüllt, REQ-015/REQ-016 umgesetzt wie in
Design §4a definiert. Warte auf User-Go für Merge.
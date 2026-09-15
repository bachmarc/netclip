# QA-Review — Story 05-01-clean-copy-selection

- **Datum:** 2026-09-15
- **QA-Manager:** QA-Gatekeeper
- **Branch:** `feature/05-01-clean-copy-selection` (Commit `8532621`, Merge-Base `b433e9e`) — Loop 1/3
- **Urteil:** ✅ **PASS** — Freigabe für Merge nach `main` (Merge nur nach User-Go)

## Geprüfte Punkte

| Prüfpunkt | Ergebnis |
|-----------|----------|
| `pytest` grün (51 bestehende + 1 neuer Test) | ✅ `52 passed, 1 warning in 0.63s` (Warning: pre-existing StarletteDeprecation, identisch zu 04-01) |
| `ruff check .` sauber | ✅ `All checks passed!` |
| REQ-014: Kopfzeile (Zeit + IP) nicht markierbar | ✅ `.kopf`-Regel (Z.39): `.kopf { color: #666; font-size: 0.85rem; margin-bottom: 0.25rem; user-select: none; }` — `.kopf` ist der Container für Zeitstempel + IP (`kopf.textContent = zeigeZeit(post.timestamp) + " · " + post.sender`, Z.115-117) — genau diese nicht markierbar |
| REQ-014: Post-Text markierbar | ✅ `.text`-Regel (Z.40): `.text { white-space: pre-wrap; overflow-wrap: anywhere; }` — kein `user-select` |
| `user-select` NICHT global | ✅ grep über `src/web/index.html`: genau **1 Treffer** (Z.39, nur in `.kopf`); kein `*`-Selektor, kein `body`, keine weitere Regel; JS-Teil ohne user-select |
| Nur 2 Dateien im Merge-Base-Diff | ✅ `git diff b433e9e..HEAD --stat`: `src/web/index.html` (1+/1−) + `tests/test_web_page.py` (38+/1−); Core/Adapter/sonstige Tests unangetastet (Target „KEINE Änderungen an src/core, src/adapters, anderen Tests" eingehalten) |
| Keine Layout/Polling/Auto-Scroll-Regression | ✅ HTML-Diff = exakt 1 CSS-Zeile (`.kopf`); JS (Polling 2 s, `since_id`, Auto-Scroll `warAmEnde`-Erkennung, `scrolleAnsEnde`, sofortiger Poll nach Aktionen) unverändert; alle 7 bestehenden Web-Tests PASSED |
| Tests-zuerst: Red-Phase plausibel & objektiv nachvollziehbar | ✅ Commit-Body: `red: neuer Test schlug fehl (user-select fehlte); stash-Nachweis: 51 passed ohne Test, 1 failed mit Test`. **QA-Simulation:** Parent-HTML (`b433e9e`, 0× user-select) ausgecheckt → exakt `test_web_index_html_kopfzeile_nicht_markierbar_text_markierbar` FAILED (`1 failed, 7 passed`) → restauriert, Workdir clean. Red-Phase belegt |
| Neuer Test strikt & deckt Story-Targets ab | ✅ `tests/test_web_page.py::test_web_index_html_kopfzeile_nicht_markierbar_text_markierbar`: (a) `user-select: none` existiert, (b) **genau 1×** (verhindert globale Mehrfach-Vergabe), (c) Regelblock-Regex ordnet es dem Selektor vor dem Block zu → assert `.kopf` in Selektor, (d) Negativ-Check: `.text`-Regelblock ohne `user-select`. Statischer Contract-Check — kein Browser, kein Netz (Testkriterium erfüllt) |
| Traceability REQ-014 → Design §4a | ✅ Design §4a: „Kopfzeile jedes Posts (Zeit + IP) erhält `user-select: none` — Maus-Markierung über mehrere Posts hinweg erfasst nur die Post-texte" — exakt umgesetzt |
| Developer Targets: nicht mehr, nicht weniger | ✅ Nur CSS-Zeile in `.kopf` + neuer Test; keine unangeforderten Features |
| Architektur-Trennung | ✅ Kein `src/core`/`src/adapters`-Kontakt; reine Frontend-/Test-Änderung |
| Branch-Hygiene | ✅ `main..HEAD`: nur `8532621 feat(05-01): …`; Planungs-Commit `b433e9e` ist Merge-Base; Commit-Message `feat(05-01):` + Metadaten-Body (symbols/breaks/affects/tests/red); Workdir clean |

## Verifikations-Logs (Summary)

```
$ git branch --show-current
feature/05-01-clean-copy-selection

$ git log main..HEAD --oneline
8532621 feat(05-01): clean copy selection — kopfzeile nicht markierbar

$ git merge-base main HEAD
b433e9e

$ git diff b433e9e..HEAD --stat
 src/web/index.html     |  2 +-
 tests/test_web_page.py | 38 +++++++++++++++++++++++++++++++++++++-
 2 files changed, 38 insertions(+), 2 deletions(-)

$ pytest
52 passed, 1 warning in 0.63s     (51 bestehende + 1 neuer; Warning pre-existing Starlette)

$ ruff check .
All checks passed!

$ grep -n "user-select" src/web/index.html
39:   .kopf { color: #666; font-size: 0.85rem; margin-bottom: 0.25rem; user-select: none; }
(1 Treffer — nur .kopf; .text Z.40 und Rest des Dokuments ohne user-select)

$ git show b433e9e:src/web/index.html | grep -c "user-select"
0  (Parent ohne user-select — Red-Phase plausibel)

$ Red-Phase-Simulation (git checkout b433e9e -- src/web/index.html)
FAILED test_web_page.py::test_web_index_html_kopfzeile_nicht_markierbar_text_markierbar
1 failed, 7 passed  → genau der neue Test ROT gegen altes HTML ✓
(Restaurierung via git checkout HEAD -- src/web/index.html; Workdir clean)

$ git commit body (8532621)
feat(05-01): clean copy selection — kopfzeile nicht markierbar
symbols: none | breaks: none | affects: src/web/index.html, tests/test_web_page.py
tests: pytest 52 passed
red: neuer Test schlug fehl (user-select fehlte); stash-Nachweis: 51 passed ohne Test, 1 failed mit Test
```

## Beobachtungen (keine FAIL-Gründe)

1. **Selektor-Matcher im neuen Test ist bewusst breit** (`([.#][\w#>\s.,:+-]*?)\{…}`): Der Regex
   matcht ab dem ersten `.`/`#` vor dem Regelblock. Funktioniert hier korrekt (`.kopf` ist der
   unmittelbare Selektor), wäre bei kaskadierten Kombinatoren (`li .kopf {}`) aber indifferent —
   die `len(treffer) == 1`-Assertion fängt globale Mehrfach-Vergaben ab. Für die aktuelle
   Contract-Prüfung ausreichend strikt.
2. **`re.findall(r"user-select\s*:\s*none", …)` matcht auch `-webkit-user-select: none`**
   (Substring). Falls künftig ein Vendor-Prefix für ältere Safari ergänzt würde, würde der
   `len == 1`-Check failen und müsste mit angepasst werden. Aktuell korrekt: 1× plain
   `user-select: none` reicht (Design §4a verlangt nur `user-select: none`; alle modernen
   Browser unprefixed).
3. **No newline at end of file** in `tests/test_web_page.py` — pre-existing Muster (Merge-Base
   endete ebenso), ruff beanstandet es nicht. Kosmetik.
4. **mypy:** Kein Projekt-Gate (s. Story 03-01: CI = pytest + ruff); mypy 2.3.0 INTERNAL ERROR
   war bereits im 04-01-Review als pre-existing Werkzeug-Problem identifiziert — nicht
   branch-verursacht, nicht Teil des Gates.

## Urteil

Alle Developer Targets exakt erfüllt — REQ-014 vollständig umgesetzt (Kopfzeile Zeit + IP via
`.kopf { user-select: none }` nicht markierbar, Post-Text `.text` markierbar, nicht global),
Red-Phase objektiv belegt, 52 Tests grün, ruff sauber, Diff minimal (2 Dateien, 1 CSS-Zeile +
1 strikter Contract-Test), keine Regressionen.
**PASS — Freigabe für Merge nach `main` nach User-Go.**
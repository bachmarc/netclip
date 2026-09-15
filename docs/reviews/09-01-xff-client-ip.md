# QA-Review — Story 09-01-xff-client-ip (REQ-018)

- **Datum:** 2026-09-15
- **Reviewer:** QA-Manager
- **Branch:** `feature/09-01-xff-client-ip` (Worktree `.worktrees/09-01-xff-client-ip`)
- **Loop:** 1/3
- **Basis:** `main` (Merge-Base `db8d6e8`)

## Urteil: **PASS**

## Checkliste

| # | Prüfpunkt | Ergebnis | Nachweis |
|---|-----------|----------|----------|
| 1 | pytest grün, Erwartung 74 passed | ✅ | `74 passed, 1 warning in 0.71s` (Warning: bekannte Starlette/httpx-Deprecation, nicht story-relevant) |
| 2 | ruff check . sauber | ✅ | `All checks passed!` |
| 3 | Helper dünn (<10 Zeilen Logik), NUR im Adapter; `src/core/` ohne IP-Logik (`sender` bleibt String-Parameter) | ✅ | Helper = 4 Zeilen Logik in `src/adapters/http.py:31-34`; `src/core/board.py` kennt nur `sender: str` als Parameter — grep über `src/core/` zeigt keinerlei Header/IP-Verarbeitung |
| 4 | Nur 2 Dateien im Merge-Base-Diff | ✅ | `src/adapters/http.py` (+13/-1) + `tests/test_http_adapter.py` (+52) |
| 5 | Fallback ohne Header unverändert | ✅ | `test_post_ohne_xff_header_behaelt_fallback_tcp_peer_ip` pinnt `testclient`; alle 70 Bestandstests grün |
| 6 | Commit-Message-Konvention + Metadaten | ✅ | `feat(09-01): ...`, Body mit `symbols/breaks/affects/tests` + Red-Phase-Angabe |
| 7 | mypy | n/a | Nicht installiert, nicht Bestandteil der CI (`ci.yml`: pytest + ruff + Docker-Build) |

## Manuelle Code-Inspektion — `_sender_ip` (statische Ableitung)

```python
xff = request.headers.get("x-forwarded-for", "")
if xff.strip():
    return xff.split(",")[0].strip()
return request.client.host
```

| Edge Case | Verhalten | Korrekt? |
|-----------|----------|----------|
| Header fehlt | `.get()` → `""` → `"".strip()` falsy → Fallback `request.client.host` | ✅ |
| `X-Forwarded-For: ""` | `""` → Fallback | ✅ |
| Nur Whitespace (`" "` bzw. `"\t"`) | `.strip()` → `""` → falsy → Fallback | ✅ |
| Einzelne IP `"192.168.111.42"` | `split(",")[0]` → `"192.168.111.42"` | ✅ |
| Kette mit Whitespace `" 192.168.111.42 , 172.22.0.1 "` | `split(",")[0]` → `" 192.168.111.42"` → `.strip()` → `"192.168.111.42"` | ✅ |
| Header-Name case-insensitivity | Test sendet `X-Forwarded-For`, Implementierung liest `x-forwarded-for` — Starlette normalisiert Header-Namen case-insensitive (lowercase Mapping); `request.headers.get` ist case-insensitive → kompatibel, von 4 grünen Tests bestätigt | ✅ |

Helper-Implementierung entspricht exakt der Developer-Target-Spezifikation
(`X-Forwarded-For` vorhanden und nicht-leer nach `.strip()` → erste Komma-IP via
`.split(",")[0].strip()`, sonst `request.client.host`).

## Sicherheits-/Design-Review (REQ-018)

- REQ-018 dokumentiert das Vertrauensmodell explizit: LAN, XFF bei Direktzugriff
  fälschbar, IP-Anzeige **informativ, kein Auth-Mechanismus**.
- Design §1 (Absender-IP) fordert genau den implementierten Helper inkl. Fallback —
  keine Validierung gefordert, erste-IP-Politik implementiert.
- Code und Docstring halten das Modell ein (Docstring nennt Spoofing-Bewusstsein).
- Keine über das Target hinausgehende Validierung (z.B. IP-Format-Checks) implementiert —
  korrekt, da laut Design nicht gefordert (Developer Targets: nicht mehr, nicht weniger).

## Tests-zuerst (Red-Phase)

- 4 neue Tests decken exakt die 4 Developer-Target-Fälle ab (einzelne IP, Proxy-Kette,
  Fallback ohne Header, Whitespace-Kette).
- Commit-Body dokumentiert: **3/4 Tests rot vor Implementierung** (Vorgänger-Code nutzte
  `request.client.host`, XFF komplett ignoriert — statisch verifiziert via
  `git show b5875f9^:src/adapters/http.py`).
- **Bewertung der Abweichung (Fallback-Test):** Angemessen und bewusst korrekt. Der
  Fallback-Test pinnt **Bestandsverhalten** (Regressionsschutz, Charakteristikum-Test) —
  er kann per Definition vor der Implementierung nicht rot sein. Die Story selbst
  verlangt die Erhaltung des Fallbacks, damit ist der Test Bestandteil der
  Anforderungssicherung, nicht der neuen Funktionalität. Red-Phase für die 3 fachlichen
  Tests plausibel und nachgewiesen (XFF-Ignoranz im Vorgänger-Commit statisch
  verifizierbar). **Kein Grund zur Beanstandung.**

## Traceability

`REQ-018` (Requirements) → Design §1 „Absender-IP (REQ-018)" → Story 09-01 →
Implementierung `src/adapters/http.py::_sender_ip` + 4 Tests. Vollständig erfüllt.

## Befunde

Keine. Keine Rückbauten, keine unangeforderten Features, keine Architekturverstöße.

**Ergebnis: PASS — Freigabe für Merge nach `main` (nach explizitem User-Go, `--no-ff`).**
# QA-Review 08-01 — GHCR-Registry-Push (Loop 1/3)

- **Datum:** 2026-09-15
- **QA-Manager:** qa-manager
- **Branch:** `feature/08-01-ghcr-push` (Worktree `.worktrees/08-01-ghcr-push`)
- **Merge-Base:** `b9f042e` (main), Feature-Commit: `cdd3eb7`
- **Urteil:** **PASS** ✅

## 1. Checkliste (alle grün)

| # | Prüfpunkt | Ergebnis |
|---|-----------|----------|
| 1 | pytest grün, Erwartung 70 passed | ✅ `70 passed, 1 warning in 0.74s` (54 Alt + 16 neu) |
| 2 | ruff check . sauber | ✅ `All checks passed!` |
| 3 | Workflow-YAML valide | ✅ `yaml.safe_load` beider Dateien OK |
| 4 | `permissions: packages: write` vorhanden, **Job-Level** | ✅ im `docker-build`-Job: `{contents: read, packages: write}` |
| 5 | Push-Guard nur main+push-Event | ✅ `${{ github.event_name == 'push' && github.ref == 'refs/heads/main' }}` |
| 6 | `needs: lint-test` — roter Lint ⇒ kein Push | ✅ `needs: lint-test` (docker-build startet nicht, wenn lint-test rot) |
| 7 | compose: `image:` UND `build: .` | ✅ beide Keys, Rest unverändert (ports, ENV, restart) |
| 8 | Nur 4 Target-Dateien im Merge-Base-Diff | ✅ ci.yml, README.md, docker-compose.yml, tests/test_ci_workflow.py (A) |
| 9 | Red-Phase-Doku plausibel | ✅ s. §4 |
| 10 | Sicherheit (Secrets, pull_request_target) | ✅ s. §6 |
| 11 | Git-Hygiene | ✅ s. §7 |
| 12 | Architektur-Trennung | ✅ kein Touch von `src/`, `Dockerfile`, `.dockerignore` |

## 2. Manuelle Workflow-Inspektion (semantisch)

### Push-Guard-Expression
```
push: ${{ github.event_name == 'push' && github.ref == 'refs/heads/main' }}
```
- **PR-Event:** `github.event_name` = `'pull_request'` ⇒ linker Operand `false`,
  `&&` short-circuits ⇒ Gesamtausdruck `false` ⇒ `push: false` — **PRs pushten nie**. ✅
- **Push auf Feature-Branch:** `github.ref` ≠ `refs/heads/main` ⇒ `false` ⇒ kein Push. ✅
- **Push auf main:** `true && true` ⇒ Push. ✅

### Step-Reihenfolge (docker-build)
```
0  checkout
1  Login to ghcr.io    (docker/login-action@v3)
2  Build and push image (docker/build-push-action@v6)
```
Login **vor** build-push. ✅

### Login-Parameter
`registry: ghcr.io`, `username: ${{ github.actor }}`, `password: ${{ secrets.GITHUB_TOKEN }}` —
exakt wie Developer Target. ✅

### Tags (raw)
```
'ghcr.io/bachmarc/netclip:latest\nghcr.io/bachmarc/netclip:${{ github.sha }}'
```
Beide Tags gesetzt: `latest` + `github.sha`. ✅

### permissions auf Job-Level
`permissions:`-Block steht **innerhalb** des `docker-build`-Jobs (nach `needs:`),
nicht global auf Workflow-Ebene — minimal privilege, `lint-test` behält Default
(read). ✅

### lint-test-Job unverändert
Diff zeigt: keine Zeile im `lint-test`-Job geändert — nur der **Datei-Header-
Kommentar** oben (Beschreibung der Story 08-01 ergänzt). Steps identisch:
checkout@v7, setup-python@v7, pip install, ruff check, pytest. Zusätzlich durch
`test_lint_test_job_untouched` abgesichert (keine ghcr-/Docker-Actions im
lint-test-Job). ✅

### docker-compose.yml Semantik
```yaml
netclip:
  image: ghcr.io/bachmarc/netclip:latest
  build: .
```
Compose-Spec erlaubt beide Keys pro Service: `docker compose pull` lädt `image:`
aus der Registry; `docker compose build` / `up --build` nutzt `build: .` lokal.
Beide Deploy-Wege (Registry ohne Repo, lokaler Build) koexistieren korrekt. ✅
Bestehende Settings unverändert: ports 8000:8000, PORT/MAX_POSTS/MAX_TEXT_LENGTH,
restart: unless-stopped (per `test_compose_yaml_valide_image_neben_build`
verifiziert).

## 3. Tests-zuerst (Red-Phase)

- Commit-Body: `red: 13 failed/3 passed (guards, login, permissions, compose-image, readme fehlten)`.
- **Arithmetisch verifiziert:** 16 neue Testmethoden in `tests/test_ci_workflow.py`;
  davon 3 auf dem Alt-Stand (main) grün (`test_workflow_yaml_parst_valide`,
  `test_docker_build_job_existiert`, `test_lint_test_job_untouched`) ⇒ exakt
  **13 failed / 3 passed** — deckt sich mit der Doku. ✅
- Tests sind statisch (YAML-Parsing + Text-Assertions): kein Docker, kein Netz,
  keine echten externen Systeme — Fake-Prinzip eingehalten; der echte Push-SMOKE
  ist laut Story der CI-Lauf selbst (Post-Merge-Verifikation durch architect/User). ✅

## 4. Gemeldete Abweichungen — Bewertung

| Abweichung | Bewertung |
|------------|-----------|
| (a) `docker/metadata-action` weggelassen | **OK.** Developer Targets (bindend: „nicht mehr/nicht weniger") listen
  sie nicht; Design §6 nennt sie nur optional („für Labels"). Weglassen korrekt. |
| (b) SHA-Tag `${{ github.sha }}` (voll) statt short-sha | **OK.** Story-Target verlangt explizit `${{ github.sha }}`; REQ-017
  fordert „Commit-SHA" — `github.sha` ist der Commit-SHA. Design-Detail
  (short-sha) weicht der normativen Story-Target-Angabe. |

## 5. Abhängigkeits-Hinweis (kein FAIL, Empfehlung für architect)

`tests/test_ci_workflow.py` importiert `yaml` (PyYAML). `requirements.txt` listet
PyYAML nicht explizit — es kommt **transitiv** über `uvicorn[standard]`
(`pyyaml>=5.1`) in die CI-Umgebung; lokal ist 6.0.2 installiert, alle 70 Tests
grün. Funktioniert nachweislich, ist aber eine implizite Abhängigkeit. Empfehlung
(kein Blocker, außerhalb dieser Story): `pyyaml` explizit in `requirements.txt`
aufnehmen, falls uvicorn-Extras je geändert werden.

## 6. Sicherheits-Check

- **Secrets:** einziger Secret-Verweis ist `${{ secrets.GITHUB_TOKEN }}` (pro-Runner
  automatisch bereitgestellt, nie im Code sichtbar). Keine hartkodierten Tokens
  (`ghp_`, `github_pat_`) im Diff. ✅
- **Kein `pull_request_target`** im Workflow (grep negativ) — keine Privilegien-
  Falle über Fork-PRs. ✅
- **Permissions minimal** auf Job-Level (nur docker-build erhält `packages: write`). ✅
- PRs bauen nur (Guard false), Login mit GITHUB_TOKEN auf PRs ist harmlos
  (reine Authentifizierung, kein Push). ✅

## 7. Git-Hygiene

- `main..HEAD` enthält genau **einen** Feature-Commit (`cdd3eb7`); Planungs-Commit
  `b9f042e` liegt bereits auf main. Kein Story-Mix. ✅
- Commit-Message: `feat(08-01): ghcr-registry-push (pullbares image)` — Konvention
  `feat(<id>)` erfüllt. ✅
- Metadaten im Body: `symbols: none | breaks: none | affects: … | tests: pytest 70
  passed | red: …` — vollständig inkl. Red-Phase-Nachweis. ✅
- Arbeitsverzeichnis clean. ✅

## 8. Offene Post-Merge-Verifikation (nicht lokal simulierbar, laut Story)

- Image `ghcr.io/bachmarc/netclip:latest` + SHA-Tag nach erstem main-Push in
  ghcr.io sichtbar (`gh api /user/packages/container/netclip/versions` oder
  Packages-Seite).
- `docker compose pull` auf zweiter LAN-Maschine (nur compose-file kopiert).
- Erstmalige Sichtbarkeit des Pakets auf **public** stellen (README dokumentiert
  den Einmal-Schritt).

Diese Punkte sind Akzeptanzkriterien, die per Story-Definition erst **nach Merge**
durch den echten CI-Lauf verifizierbar sind — lokal korrekt als nicht simulierbar
markiert, kein FAIL-Grund.

## Urteil

**PASS** — Freigabe für Merge nach `main` (nur nach explizitem User-Go, empfohlen
als `git merge --no-ff feature/08-01-ghcr-push`). Keine Fix-Aufträge.
# Story 08-01 — GHCR-Registry-Push (pullbares Image)

Status: Geplant
Traceability: REQ-017 → Design §6 (Registry-Push)

## Definition

CI pusht das Docker-Image bei jedem Push auf `main` nach `ghcr.io` (GitHub Container
Registry). Das Image wird pullbar — Deployment auf LAN-Rechnern per
`docker compose pull && docker compose up -d` ohne Repo-Clone/-Build.

## Entwicklungsziel

`ghcr.io/bachmarc/netclip:latest` existiert, wird bei jedem grünen CI-Lauf aktualisiert
(Tags: `latest` + Short-SHA) und ist im LAN pullbar.

## Developer Targets (exakt, nicht mehr/nicht weniger)

- [ ] `.github/workflows/ci.yml` — `docker-build`-Job erweitern:
  - Job-Level: `needs: lint-test` (nur grüner Lint+Test pusht) + `permissions: { contents: read, packages: write }`
  - Login: `docker/login-action@v3` mit `registry: ghcr.io`, `username: ${{ github.actor }}`, `password: ${{ secrets.GITHUB_TOKEN }}`
  - Build+Push: `docker/build-push-action@v6` mit context `.`, `push: true`, Tags `ghcr.io/bachmarc/netclip:latest` + `ghcr.io/bachmarc/netclip:${{ github.sha }}` auf `push.main` (auf PRs nur Build, kein Push — Guard: `github.event_name == 'push' && github.ref == 'refs/heads/main'`)
  - Keine Änderung am `lint-test`-Job
- [ ] `docker-compose.yml` — ERGÄNZEN (nicht ersetzen): `image: ghcr.io/bachmarc/netclip:latest` neben dem bestehenden `build: .`
- [ ] `README.md` — Deployment-Sektion um Registry-Variante ergänzen (`docker compose pull && docker compose up -d`); Hinweis: erster Pull braucht Sichtbarkeit des Pakets (public) — Einmaligkeit der Freigabe in GitHub → Packages → Settings → Change visibility
- [ ] KEINE Änderungen an: `src/`, `tests/`, `Dockerfile`, `.dockerignore`

## Akzeptanzkriterien (prüft QA-Manager)

- [ ] Workflow-YAML valide; `permissions: packages: write` vorhanden; PRs pushten NIEMALS (Guard)
- [ ] Push auf `main` → Image mit Tags `latest` + SHA in ghcr.io sichtbar (Verifikation via `gh api /user/packages/container/netclip/versions` oder Packages-Seite)
- [ ] `docker compose pull` funktioniert auf einer zweiten Maschine (ohne Repo-Clone: compose-file kopiert reicht)
- [ ] `lint-test` rot → KEIN Push (needs-Kette)
- [ ] Lokal unverändert testbar: 54 Tests grün, ruff sauber, `docker compose build` (build-Pfad bleibt)

## Testkriterien (müssen VOR Implementierung existieren)

- [ ] Statische YAML-Verifikation: `python3 -c "import yaml; yaml.safe_load(open('.github/workflows/ci.yml'))"` — vor/nach
- [ ] Guard-Check als Text-Assertion: Workflow enthält Push-Bedingung nur für `main` + `push: true` erst nach Login
- [ ] Echter Push-SMOKE = der CI-Lauf selbst auf GitHub (Verifikation nach Merge durch architect/User via Packages-Seite) — nicht lokal simulierbar
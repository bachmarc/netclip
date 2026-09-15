# STORIES.md — Story-Index (NetClip)

> Stories in Phase 2 im Dialog freigegeben. Reihenfolge = Wellen (parallel, wo angegeben).

## Phasen

| Phase | Fokus | Stories |
|-------|-------|---------|
| 0 | Foundation | 00-01-setup |
| 1 | Core | 01-01-core-board |
| 2 | UI/Integration | 02-01-http-api (∥ 02-02), 02-02-web-frontend |
| 3 | Deployment | 03-01-docker-ci |

## Index

| Story | Titel | Status | Branch | Traceability |
|-------|-------|--------|--------|--------------|
| [00-01-setup](docs/stories/00-01-setup.md) | Projekt-Setup (Infrastruktur) | Erledigt (QA-PASS) | `feature/00-01-setup` | NFR-004 → §7 |
| [01-01-core-board](docs/stories/01-01-core-board.md) | Core: FakeClock + PostBoard | Erledigt (QA-PASS, Loop 1) | `feature/01-01-core-board` | REQ-002/004/005/006/007/010/011 → §1, §3 |
| [02-01-http-api](docs/stories/02-01-http-api.md) | FastAPI-Adapter (API) | Erledigt (QA-PASS, Loop 2) | `feature/02-01-http-api` | REQ-001/003/009/012 → §1, §4 |
| [02-02-web-frontend](docs/stories/02-02-web-frontend.md) | Frontend (Seite + Polling) | Erledigt (QA-PASS, Loop 1) | `feature/02-02-web-frontend` | REQ-002/003/004/005/006/009 → §4a |
| [03-01-docker-ci](docs/stories/03-01-docker-ci.md) | Docker + GitHub Actions CI | Erledigt (QA-PASS, Loop 1; Docker-SMOKE ✓) | `feature/03-01-docker-ci` | NFR-001/003 → §6 |

## QA-Protokolle

Alle Reviews unter `docs/reviews/`: 00-01-setup.md, 01-01-core-board.md,
02-01-http-api.md (Loop 1 FAIL → Loop 2 PASS), 02-02-web-frontend.md, 03-01-docker-ci.md.

## Merge-Reihenfolge & QA (tatsächlicher Ablauf)

1. **Welle 1**: `00-01-setup` → QA-PASS → Merge `96857d6`
2. **Welle 2**: `01-01-core-board` → QA-PASS → Merge `e618327`
3. **Welle 3**: `02-01-http-api` → QA-FAIL (Bodies→500) → Fix → QA-PASS Loop 2 → Merge `d38c912`
4. **Welle 4** (parallel, je eigener Worktree): `02-02-web-frontend` + `03-01-docker-ci` → QA-PASS je Story → Merges `a595ab4`/`b434fa9`
5. **Abschluss**: Docker-Build-SMOKE erfolgreich (Image `netclip:0.1.0`, GET / 200, POST/GET-Post OK, non-root)

Regeln: Jede Story = eigener Branch `feature/<story-id>-<slug>`, kein direkter Push auf `main`.
Commit-Body: `symbols: … | breaks: … | affects: … | tests: …`. QA-Gate: PASS → Merge, FAIL → Fix-Loop (max. 3), dann BLOCKED.
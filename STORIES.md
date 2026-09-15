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
| [00-01-setup](docs/stories/00-01-setup.md) | Projekt-Setup (Infrastruktur) | Geplant | `feature/00-01-setup` | NFR-004 → §7 |
| [01-01-core-board](docs/stories/01-01-core-board.md) | Core: FakeClock + PostBoard | Geplant | `feature/01-01-core-board` | REQ-002/004/005/006/007/010/011 → §1, §3 |
| [02-01-http-api](docs/stories/02-01-http-api.md) | FastAPI-Adapter (API) | Geplant | `feature/02-01-http-api` | REQ-001/003/009/012 → §1, §4 |
| [02-02-web-frontend](docs/stories/02-02-web-frontend.md) | Frontend (Seite + Polling) | Geplant | `feature/02-02-web-frontend` | REQ-002/003/004/005/006/009 → §4a |
| [03-01-docker-ci](docs/stories/03-01-docker-ci.md) | Docker + GitHub Actions CI | Geplant | `feature/03-01-docker-ci` | NFR-001/003 → §6 |

## Merge-Reihenfolge & QA

1. **Welle 1**: `00-01-setup` → QA → Merge
2. **Welle 2**: `01-01-core-board` → QA → Merge
3. **Welle 3** (parallel auf develop-Stand): `02-01-http-api` **und** `02-02-web-frontend` → QA je Story → Merge
4. **Welle 4**: `03-01-docker-ci` → QA → Merge

Regeln: Jede Story = eigener Branch `feature/<story-id>-<slug>`, kein direkter Push auf `main`.
Commit-Body: `symbols: … | breaks: … | affects: … | tests: …`. QA-Gate: PASS → Merge, FAIL → Fix-Loop (max. 3), dann BLOCKED.
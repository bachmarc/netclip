# STORIES.md — Story-Index (NetClip)

> Stories in Phase 2 im Dialog freigegeben. Reihenfolge = Wellen (parallel, wo angegeben).

## Phasen

| Phase | Fokus | Stories |
|-------|-------|---------|
| 0 | Foundation | 00-01-setup |
| 1 | Core | 01-01-core-board |
| 2 | UI/Integration | 02-01-http-api (∥ 02-02), 02-02-web-frontend |
| 3 | Deployment | 03-01-docker-ci |
| 4 | Replanning (User-Feedback) | 04-01-chat-layout |
| 5 | UX-Feinschliff | 05-01-clean-copy-selection |
| 6 | UX-Fixes (User-Feedback) | 06-01-send-guard-autogrow |
| 7 | CI-Reparatur | 07-01-ci-fix (direkt, kein QA-Loop) |
| 8 | Registry-Deployment | 08-01-ghcr-push |
| 9 | Reverse-Proxy-Support | 09-01-xff-client-ip |

## Index

| Story | Titel | Status | Branch | Traceability |
|-------|-------|--------|--------|--------------|
| [00-01-setup](docs/stories/00-01-setup.md) | Projekt-Setup (Infrastruktur) | Erledigt (QA-PASS) | `feature/00-01-setup` | NFR-004 → §7 |
| [01-01-core-board](docs/stories/01-01-core-board.md) | Core: FakeClock + PostBoard | Erledigt (QA-PASS, Loop 1) | `feature/01-01-core-board` | REQ-002/004/005/006/007/010/011 → §1, §3 |
| [02-01-http-api](docs/stories/02-01-http-api.md) | FastAPI-Adapter (API) | Erledigt (QA-PASS, Loop 2) | `feature/02-01-http-api` | REQ-001/003/009/012 → §1, §4 |
| [02-02-web-frontend](docs/stories/02-02-web-frontend.md) | Frontend (Seite + Polling) | Erledigt (QA-PASS, Loop 1) | `feature/02-02-web-frontend` | REQ-002/003/004/005/006/009 → §4a |
| [03-01-docker-ci](docs/stories/03-01-docker-ci.md) | Docker + GitHub Actions CI | Erledigt (QA-PASS, Loop 1; Docker-SMOKE ✓) | `feature/03-01-docker-ci` | NFR-001/003 → §6 |
| [04-01-chat-layout](docs/stories/04-01-chat-layout.md) | Chat-Layout: chronologisch, Eingabe unten | Erledigt (QA-PASS, Loop 1; User-Go nach Planungs-Checkpoint) | `feature/04-01-chat-layout` | REQ-013 → §4a (rev.) |
| [05-01-clean-copy-selection](docs/stories/05-01-clean-copy-selection.md) | Copy ohne Zeitstempel/IP (`user-select: none`) | Erledigt (QA-PASS, Loop 1; User-Go nach Planungs-Checkpoint) | `feature/05-01-clean-copy-selection` | REQ-014 → §4a |
| [06-01-send-guard-autogrow](docs/stories/06-01-send-guard-autogrow.md) | Send-Guard + Auto-Grow-Textarea | Erledigt (QA-PASS, Loop 1; User-Go nach Planungs-Checkpoint) | `feature/06-01-send-guard-autogrow` | REQ-015, REQ-016 → §4a |
| [07-01-ci-fix](docs/reviews/00-01-setup.md) | CI grün: ruff-Pin + Node-24-Actions | Erledigt (direkte Umsetzung nach User-Go; CI-Verifikation grün) | `main` (8d38bda) | CI-Stabilität → §6 |
| [08-01-ghcr-push](docs/stories/08-01-ghcr-push.md) | GHCR-Registry-Push (pullbares Image) | Erledigt (QA-PASS, Loop 1; User-Go; Registry-Pull verifiziert) | `feature/08-01-ghcr-push` | REQ-017 → §6 |
| [09-01-xff-client-ip](docs/stories/09-01-xff-client-ip.md) | Echte Client-IP hinter Reverse-Proxy (XFF) | Geplant | `feature/09-01-xff-client-ip` | REQ-018 → §1 |
| [09-02-clear-version-sync](docs/stories/09-02-clear-version-sync.md) | Clear-Sync: Version statt consume-once | Geplant | `feature/09-02-clear-version-sync` | REQ-019 → §4, §4a |

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
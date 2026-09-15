# NetClip — LAN-Zwischenablage

> Winziger Webserver für das interne Netz: Text posten, jeder sieht ihn sofort.
> RAM-only — nichts wird persistiert. Für Texte, Befehle und Infos zwischen
> Arbeitsplätzen, wenn Zwischenablagen versagen.

## Features

- Textfeld + „Senden" → Post erscheint bei allen Clients im LAN (Polling ~2 s)
- Jeder Post zeigt Sendezeit + Absender-IP — kein Login, keine Nicknames
- „Clear all" / „Clear last" löschen für alle Clients
- Keine Persistenz: Restart = leere Liste; FIFO-Limit (Default 3000 Posts)
- Textlimit pro Post: Default 100.000 Zeichen (~mehrere DIN-A4-Seiten)
- Docker-Deployment, GitHub Actions CI

## Status

- [x] Phase 0: Folder + Git eingerichtet
- [x] Phase 1: Requirements & Design (`docs/requirements.md`, `docs/design.md`)
- [ ] Phase 2: Stories (`STORIES.md`, `docs/stories/`)
- [ ] Phase 3: Tests zuerst
- [ ] Phase 4: Implementierung (Feature-Branches)
- [ ] Phase 5: QA-Gate

## Struktur

```
docs/            requirements.md, design.md, stories/
src/core/        Reine Logik (PostBoard) — null Framework/IO-Imports, voll unit-testbar
src/adapters/    FastAPI-Wrapper — liest Request, delegiert an Core, schreibt Antwort
src/web/         Statische Seite (HTML+JS, Deutsch), Polling-Client
tests/fakes/     Fake-Interfaces (FakeClock) für alle externen Abhängigkeiten
```

## Betrieb (später, nach Implementierung)

```bash
docker compose up        # erreichbar unter http://<host>:8000
```

Konfiguration per ENV: `PORT` (8000), `MAX_POSTS` (3000), `MAX_TEXT_LENGTH` (100000).

## Entwicklung

Jede Story = eigener Branch `feature/<story-id>-<slug>`.
Merge nach `main` nur nach QA-Gate. Siehe `AGENTS.md` und `STORIES.md`.
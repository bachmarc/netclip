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
- [x] Phase 2: Stories (`STORIES.md`, `docs/stories/`)
- [x] Phase 3: Tests zuerst (Fake-basiert, vor Implementierung)
- [x] Phase 4: Implementierung (Feature-Branches, alle Stories erledigt)
- [x] Phase 5: QA-Gate (alle Stories PASS; 48 Tests grün; Docker-SMOKE erfolgreich)

## Struktur

```
docs/            requirements.md, design.md, stories/
src/core/        Reine Logik (PostBoard) — null Framework/IO-Imports, voll unit-testbar
src/adapters/    FastAPI-Wrapper — liest Request, delegiert an Core, schreibt Antwort
src/web/         Statische Seite (HTML+JS, Deutsch), Polling-Client
tests/fakes/     Fake-Interfaces (FakeClock) für alle externen Abhängigkeiten
```

## Betrieb

### Docker (empfohlen)

```bash
docker compose up        # baut Image, startet Container → http://<host>:8000
```

Der Container läuft als non-root User; `restart: unless-stopped` hält NetClip
über Neustarts hinweg aktiv.

### Docker (Registry-Image, ohne Repo-Clone)

Bei jedem Push auf `main` baut die CI das Image und pusht es nach
`ghcr.io/bachmarc/netclip` (Tags: `latest` + Commit-SHA). Auf LAN-Rechnern
reicht daher die `docker-compose.yml` — kein Repo-Clone, kein lokaler Build:

```bash
docker compose pull && docker compose up -d
```

**Hinweis zur ersten Inbetriebnahme:** Das Paket ist anfangs privat. Ein Pull
erfordert, dass die Paket-Sichtbarkeit auf **public** gestellt wurde — einmalig
unter *GitHub → Packages → netclip → Package settings → Change visibility*.
(Der Pull selbst authentifiziert sich sonst gegen die Registry; public stellt
das Paket jedem im LAN ohne Login bereit.)

### Manuell (Python 3.12+)

```bash
pip install -r requirements.txt
python -m src.adapters.main
```

### Konfiguration per ENV

| ENV-Variable       | Default  | Bedeutung                                    |
|--------------------|----------|----------------------------------------------|
| `PORT`             | `8000`   | HTTP-Port (uvicorn, host `0.0.0.0`)          |
| `MAX_POSTS`        | `3000`   | FIFO-Limit — älteste Posts fallen heraus     |
| `MAX_TEXT_LENGTH`  | `100000` | Maximale Zeichen pro Post                    |

Die Defaults entsprechen dem Code in `src/adapters/main.py` (`build_app()`);
`docker-compose.yml` setzt dieselben Werte explizit.

## Entwicklung

Jede Story = eigener Branch `feature/<story-id>-<slug>`.
Merge nach `main` nur nach QA-Gate. Siehe `AGENTS.md` und `STORIES.md`.
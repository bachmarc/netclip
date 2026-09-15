# Requirements — NetClip (LAN-Zwischenablage)

> Source of Truth, freigegeben im Dialog (Phase 1).

## Problem & Zielgruppe

**Problem:** Zwischen Arbeitsplätzen im internen Netz müssen regelmäßig kurze bis mittlere Texte
(Befehle, Passwörter, Snippets, Infos) ausgetauscht werden. Wenn Zwischenablagen zwischen
Geräten/Sessions nicht funktionieren (RDP-Clipboard, VMs, verschiedene OS), fehlt ein
unkomplizierter Weg.

**Zielgruppe:** Nutzer im eigenen LAN (privat/Team). Kein Login, kein Verwaltungsaufwand.

**Lösung:** Winziger Webserver im LAN — Browser öffnen, Text posten, jeder sieht es sofort.
RAM-only: Nach Restart (oder „Clear all") ist alles weg. Kein Langzeit-Chat-Archiv.

## Funktionale Requirements

| ID | Requirement | Priorität |
|----|-------------|-----------|
| REQ-001 | Webserver hostet Seite im LAN (HTTP, erreichbar per IP/Hostname) | Muss |
| REQ-002 | Textfeld (Tippen/Einfügen) + „Send"-Button → neuer Post erscheint in der Liste | Muss |
| REQ-003 | Jeder Client im LAN sieht alle Posts | Muss |
| REQ-004 | Jeder Post zeigt Sendezeit und Absender-IP | Muss |
| REQ-005 | „Clear all"-Taste löscht alle Posts für alle Clients | Muss |
| REQ-006 | „Clear last"-Taste löscht den letzten Post für alle Clients | Nice-to-have |
| REQ-007 | Posts nur im RAM — keine Persistenz; Restart = leere Liste | Muss |
| REQ-008 | Kein Login, keine Nicknames — Zeitstempel + IP als Absenderkennung | Muss |
| REQ-009 | Live-Update via Polling (~2 s Intervall), neue Posts erscheinen ohne Reload in geöffneten Tabs | Muss |
| REQ-010 | Max. 3000 Posts (FIFO, älteste fliegen raus); Default per ENV `MAX_POSTS` konfigurierbar | Muss |
| REQ-011 | Max. 100.000 Zeichen pro Post (~mehrere DIN-A4-Seiten); Default per ENV `MAX_TEXT_LENGTH` konfigurierbar; Überschreiten → Fehler mit Hinweis | Muss |
| REQ-012 | Polling-Optimierung: Client fragt nur Posts seit letzter bekannter ID ab (`since_id`) | Muss |
| REQ-013 | Chat-Layout: Eingabebereich (Textfeld + Buttons) **unten fixiert**; Post-Liste chronologisch — **neueste ganz unten**; Liste scrollbar zum Hochscrollen älterer Posts; bei neuen Posts Auto-Scroll ans untere Ende (nur wenn Nutzer nicht manuell hochgescrollt hat) | Muss |
| REQ-014 | Maus-Markierung kopierbar über mehrere Posts hinweg — **ohne Zeitstempel und IP**: Kopfzeile (Zeit + IP) ist nicht markierbar (`user-select: none`), nur Post-Texte landen in der Auswahl/Zwischenablage | Muss |
| REQ-015 | Keine doppelten Posts durch Mehrfach-Klick: „Senden" ist während eines laufenden Requests deaktiviert (Guard); ein Doppel-/Mehrfachklick erzeugt genau einen Post | Muss |
| REQ-016 | Eingabefeld wächst mit dem Text mit (auto-resize): Ab der vorletzten Zeile vergrößert sich die Textarea (bis max. ~40vh), scrollt intern wenn der Text höher wird; verkleinert sich beim Leeren/Reset wieder auf die Ausgangshöhe | Muss |
| REQ-017 | CI pusht das Docker-Image bei jedem Push auf `main` nach `ghcr.io` (Tags: `latest` + Commit-SHA); das Image ist pullbar (`docker compose pull`) — Deploy auf LAN-Rechnern ohne Repo-Clone/-Build | Muss |
| REQ-018 | Echte Client-IP hinter Reverse-Proxy: Absenderkennung = erste IP aus `X-Forwarded-For`, falls Header vorhanden; sonst TCP-Peer (`request.client.host`). Vertrauensmodell LAN — XFF ist bei Direktzugriff fälschbar, die IP-Anzeige ist informativ, kein Auth-Mechanismus | Muss |

## Nicht-funktionale Requirements

| ID | Requirement | Priorität |
|----|-------------|-----------|
| NFR-001 | Minimaler Betrieb: start → läuft; nur Port (und Limits) konfigurierbar | Muss |
| NFR-002 | Kernlogik (Board) vollständig unit-testbar ohne echten Server/Netzwerk (Fakes) | Muss |
| NFR-003 | Docker-Deployment; GitHub Actions CI (pytest + ruff + Docker-Build) | Muss |
| NFR-004 | UI-Texte Deutsch; Code/Bezeichner Englisch | Muss |
| NFR-005 | HTTP im internen Netz — bewusst ohne TLS (siehe Abgrenzung) | Muss |

## Abgrenzung (NICHT Bestandteil)

- **Keine Persistenz** — kein Archiv, keine Historie über Restart hinaus (expliziter Wunsch)
- **Kein Login/Auth** — Vertrauensmodell: internes LAN
- **Kein TLS/HTTPS** — internes Netz; Passwörter werden bewusst nur manuell per Clear all entfernt (kein Auto-Clear)
- **Keine Nicknames/User-Accounts** — Zeit + IP genügen als Absenderkennung
- **Kein Langzeit-Chat** — FIFO-Limit 3000 Posts; kein Threading, keine Suchfunktion
- **Keine Attachments/Dateien** — nur Text

## Offene Fragen

- Keine — alle im Interview geklärt.
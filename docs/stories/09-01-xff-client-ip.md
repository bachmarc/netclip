# Story 09-01 — Echte Client-IP hinter Reverse-Proxy (X-Forwarded-For)

Status: Geplant
Traceability: REQ-018 → Design §1 (Absender-IP)

## Definition

Hinter einem Reverse-Proxy (Nginx Proxy Manager im Docker-Netz) erscheint als Absender
nur die Proxy-Container-IP (z.B. `172.22.0.1`). Fix: Absenderkennung nutzt den
`X-Forwarded-For`-Header (erste IP der Kette), Fallback bleibt die TCP-Peer-IP.

## Entwicklungsziel

Posts zeigen hinter dem Proxy die echte Client-IP; Direktzugriff ohne Proxy unverändert.

## Developer Targets (exakt, nicht mehr/nicht weniger)

- [ ] `tests/test_http_adapter.py` — ERST erweitern (vor Implementierung, Red-Phase via git stash):
  - `POST /api/posts` mit Header `X-Forwarded-For: "192.168.111.42"` → Post-Sender ist `192.168.111.42`
  - `POST /api/posts` mit Header `X-Forwarded-For: "192.168.111.42, 172.22.0.1"` (Proxy-Kette) → Sender ist `192.168.111.42` (erste IP)
  - `POST /api/posts` OHNE Header → Sender bleibt `testclient` (bestehendes Verhalten, Fallback)
  - Header mit Whitespace um IPs (`" 192.168.111.42 , 172.22.0.1 "`) → geparst `192.168.111.42`
- [ ] `src/adapters/http.py` — anpassen:
  - Helper `def _sender_ip(request: Request) -> str:` — liest `X-Forwarded-For`;
    falls vorhanden und nicht-leer nach `.strip()`: erste durch Komma getrennte IP
    (`.split(",")[0].strip()`), sonst `request.client.host`
  - `POST /api/posts` nutzt `_sender_ip(request)` statt `request.client.host`
  - KEINE weiteren Änderungen (Routen, Validierung, Fehlerbehandlung, Clear unverändert)
- [ ] KEINE Änderungen an: `src/core/`, anderen Adapter-Dateien, anderen Tests

## Akzeptanzkriterien (prüft QA-Manager)

- [ ] pytest grün (Erwartung: 70 bestehende + 4 neue Tests)
- [ ] ruff check . sauber
- [ ] Helper dünn (<10 Zeilen), nur im Adapter (Core ohne IP-Logik — `sender` bleibt nur Parameter)
- [ ] Nur `src/adapters/http.py` + `tests/test_http_adapter.py` im Diff
- [ ] Bestehende Tests unverändert grün (insbesondere Fallback-Fall ohne Header)

## Testkriterien (müssen VOR Implementierung existieren)

- [ ] 4 neue Tests laufen zuerst ROT (aktueller Code ignoriert XFF komplett)
- [ ] TestClient-Tests ohne Netz — Header-Injektion simuliert den Proxy
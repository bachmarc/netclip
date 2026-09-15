# Design — <Projektname>

> **Entwurf — wird im Dialog (Phase 1) mit dem User finalisiert.**

## 1. Architektur: Funktion vs Konnektivität

### `src/core/` — Funktion (reine Logik)

- Null Imports aus Framework/IO/HA/DB/API.
- Bekommt alles als Parameter, gibt Dicts/Primitives zurück.
- Simulation-Helper für Tests (z.B. `simuliere_aktiv()`).

### `src/adapters/` — Konnektivität (dünne Wrapper)

- 3-10 Zeilen pro Methode: Lesen → Core delegieren → Schreiben.
- Timer/Listener/Scheduler ausschließlich hier.

## 2. Fake-Interfaces (PFLICHT für jede externe Abhängigkeit)

| Externes System | Fake | Ort |
|-----------------|------|-----|
| TBD | `FakeTBD` | `tests/fakes/` |

## 3. Datenmodell

- TBD

## 4. API-Skizze

- TBD

## 5. Fehlerbehandlung

- TBD

## 6. Deployment

- TBD

## 7. Versionierung

- `APP_VERSION = "0.1.0"` (Modul `src/version.py`), Semantic Versioning.
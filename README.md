# <Projektname>

> Kurze Projektbeschreibung — wird nach dem Requirements-Interview ausgefüllt.

## Status

- [x] Phase 0: Folder + Git eingerichtet
- [ ] Phase 1: Requirements & Design (`docs/requirements.md`, `docs/design.md`)
- [ ] Phase 2: Stories (`STORIES.md`, `docs/stories/`)
- [ ] Phase 3: Tests zuerst
- [ ] Phase 4: Implementierung (Feature-Branches)
- [ ] Phase 5: QA-Gate

## Struktur

```
docs/            requirements.md, design.md, stories/
src/core/        Reine Logik — null Framework/IO-Imports, voll unit-testbar
src/adapters/    Dünne Wrapper zu externen Systemen (3-10 Zeilen pro Methode)
tests/fakes/     Fake-Interfaces für alle externen Abhängigkeiten
```

## Entwicklung

Jede Story = eigener Branch `feature/<story-id>-<slug>`.
Merge nach `main` nur nach QA-Gate. Siehe `AGENTS.md` und `STORIES.md`.
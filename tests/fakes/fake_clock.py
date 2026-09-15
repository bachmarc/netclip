"""Fake-Interface für die Systemuhr (Pflicht laut Design §2).

Deterministische, tick-bare Uhr für Core-Tests — kein ``datetime.now()`` im Test-Pfad.
Läuft ohne externe Systeme, nur stdlib.
"""

from __future__ import annotations

from datetime import datetime, timedelta, timezone

DEFAULT_START = datetime(2026, 1, 1, 12, 0, 0, tzinfo=timezone.utc)


class FakeClock:
    """Deterministische Uhr: startet bei ``2026-01-01T12:00:00+00:00`` (UTC)."""

    def __init__(self, start: datetime | None = None) -> None:
        self._now = start if start is not None else DEFAULT_START

    def now(self) -> datetime:
        """Aktuelle Fake-Zeit (timezone-aware, UTC)."""
        return self._now

    def tick(self, seconds: int = 1) -> None:
        """Rückt die Fake-Zeit um ``seconds`` Sekunden vor."""
        self._now = self._now + timedelta(seconds=seconds)
"""NetClip Core: PostBoard — reine Board-Logik ohne Framework/IO.

Null Imports aus FastAPI/HTTP/Netz/DB — nur stdlib (``collections``, ``datetime``, ``typing``).
Zeit kommt ausschließlich als Parameter (``now``); Konfiguration (``max_posts``,
``max_text_length``) per Konstruktor. RAM-only: keine Persistenz, kein Timer.
"""

from __future__ import annotations

from collections import deque
from datetime import UTC, datetime

DEFAULT_SIMULATION_TIME = datetime(2026, 1, 1, 12, 0, 0, tzinfo=UTC)


class PostBoard:
    """LAN-Zwischenablage im RAM: Posts anlegen, abrufen, clearen (FIFO-Limit)."""

    def __init__(self, max_posts: int = 3000, max_text_length: int = 100_000) -> None:
        self._posts: deque[dict] = deque(maxlen=max_posts)
        self._max_text_length = max_text_length
        self._next_id = 1
        self._clear_version = 0

    # --- Write ---------------------------------------------------------------

    def add_post(self, text: str, sender: str, now: datetime) -> dict:
        """Neuen Post anlegen. Validiert Text; bei Verstoß ``ValueError`` (deutsch)."""
        if not text.strip():
            raise ValueError("Text darf nicht leer sein.")
        if len(text) > self._max_text_length:
            raise ValueError(
                f"Text ist zu lang (maximal {self._max_text_length} Zeichen erlaubt)."
            )
        post = {
            "id": self._next_id,
            "text": text,
            "timestamp": now.isoformat(),
            "sender": sender,
        }
        self._next_id += 1
        self._posts.append(post)
        return post

    # --- Clear ---------------------------------------------------------------

    def clear_all(self) -> None:
        """Entfernt alle Posts und inkrementiert die Clear-Version (REQ-019)."""
        self._posts.clear()
        self._clear_version += 1

    def clear_last(self) -> None:
        """Entfernt den letzten Post (falls vorhanden) und inkrementiert die Version."""
        if self._posts:
            self._posts.pop()
        self._clear_version += 1

    @property
    def clear_version(self) -> int:
        """Monotoner Zähler, inkrementiert bei jedem clear_all/clear_last."""
        return self._clear_version

    # --- Read ----------------------------------------------------------------

    def get_posts(self, since_id: int = 0) -> list[dict]:
        """Posts mit ``id > since_id``, aufsteigend sortiert. ``since_id=0`` → alle."""
        return [post for post in self._posts if post["id"] > since_id]

    # --- Simulation-Helper -----------------------------------------------------

    def simuliere_post(
        self, text: str = "test", sender: str = "test-ip", now: datetime | None = None
    ) -> dict:
        """Test-Helper: fügt Post hinzu; nutzt FakeClock-Default-Zeit, falls ``now=None``."""
        if now is None:
            now = DEFAULT_SIMULATION_TIME
        return self.add_post(text, sender, now)
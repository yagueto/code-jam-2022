from typing import Protocol


class Game(Protocol):
    """Handle all game backend logic."""

    def phase_start(self) -> None:
        """Report that the phase has started."""
        ...

    def update(self, data) -> (list, dict):
        """Send update information to the current phase."""
        ...

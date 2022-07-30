import pathlib
from typing import Dict

from fastapi import WebSocket

from phases import first_phase


class Game:
    """Handle all game backend logic."""

    phase = None
    players: Dict[WebSocket, str]
    connection_manager = None

    def __init__(self, players: Dict[WebSocket, str], connection_manager) -> None:
        self.players = players
        self.phase = first_phase.FirstPhase(
            players=players, images_dir=pathlib.Path.cwd().joinpath("phases", "bugs")
        )

    def game_start(self):
        """Start phase"""
        return self.phase.start()

    def receive(self, data):
        """Send update information to the current phase."""
        print(data)

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

    def receive(self, websocket, data):
        """Send update information to the current phase."""
        return self.phase.receive(websocket, data)

    def end_game(self):
        """Collects the game metrics for each player and ..."""
        self.metrics = {}
        for player_socket in self.players:
            metric = self.phase.submissions[player_socket][2]
            self.metrics[player_socket] = metric

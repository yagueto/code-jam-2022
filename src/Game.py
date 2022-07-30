import pathlib
from typing import Dict, List

from fastapi import WebSocket

from phases import first_phase


class Game:
    """Handle all game backend logic."""

    phase = 0
    phases: List
    players: Dict[WebSocket, str]
    connection_manager = None
    metrics: Dict[int, list]

    def __init__(self, players: Dict[WebSocket, str], connection_manager) -> None:
        self.players = players
        self.phases = [
            first_phase.FirstPhase(players=players, images_dir=pathlib.Path.cwd().joinpath("phases", "bugs")),
        ]
        self.connection_manager = connection_manager

    def game_start(self):
        """Start phase"""
        return self.phases[self.phase].start()

    def receive(self, websocket, data):
        """Send update information to the current phase."""
        self.phases[self.phase].receive(websocket, data)
        if self.phases[self.phase].is_finished:
            return self.end_phase()

    def end_phase(self):
        """Collects the game metrics for each player and ..."""
        dif = self.phases[self.phase].get_next_level_difficulty()
        self.phase += 1
        if len(self.phases) <= self.phase:
            return  # TODO: Call statistics site from here
        self.phases[self.phase].start(dif)

        return self.connection_manager.send(self.players.keys(), {"type": "phase_end"})

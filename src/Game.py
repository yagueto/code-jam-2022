import pathlib
from typing import Dict, List

from fastapi import WebSocket

from phases import first_phase, second_phase


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
            first_phase.FirstPhase(
                players=players,
                images_dir=pathlib.Path.cwd().joinpath("phases", "bugs"),
            ),
            second_phase.SecondPhase(
                players=players,
                image_dir=pathlib.Path.cwd().joinpath("phases", "bugs", "ant_contour.png"),
            ),
        ]
        self.connection_manager = connection_manager

    def game_start(self):
        """Start phase"""
        return self.phases[self.phase].start()

    def receive(self, websocket, data):
        """Send update information to the current phase."""
        if self.phases[self.phase].is_finished:
            return self.end_phase()
        return self.phases[self.phase].receive(websocket, data)

    def start_next_phase(self):
        """Start the current phase."""
        dif = self.phases[self.phase].get_next_level_difficulty()
        self.phase += 1
        return self.phases[self.phase].start(dif)

    def end_phase(self):
        """Collects the game metrics for each player and ..."""
        if len(self.phases) <= self.phase:
            return  # TODO: Call statistics site from here

        return {
            "type": "phase_end",
            "user": self.players.keys(),
            "data": {
                "phase": self.phase + 1,
            },
        }

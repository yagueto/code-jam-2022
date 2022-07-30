import pathlib

from fastapi import WebSocket

Metrics = dict[int, dict[WebSocket, float]]


class StatsPhase:
    """Manages game stats and send them to frontend."""

    def __init__(self, players: dict[WebSocket, str], csv_path: pathlib.Path) -> None:
        self.players = players
        self.csv_path = csv_path

    def start(self, metrics: Metrics):
        """Reads the metrics and save them in a csv file."""
        pass

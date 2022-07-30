import math
from typing import Any

from fastapi import WebSocket

Metrics = dict[int, dict[WebSocket, float]]


class StatsPhase:
    """Manages game stats and send them to frontend."""

    def __init__(self, players: dict[WebSocket, str]) -> None:
        self.players = players

    def generate_stats_resume(self, metrics: Metrics) -> list[list[Any]]:
        """Reads the metrics and save them in a csv file."""
        results = [["Player_ID", "Phase_1", "Phase_2", "Total"], ]
        for player_socket, player_id in self.players.items():
            metric_1 = metrics[0][player_socket]
            metric_2 = metrics[1][player_socket]

            if metric_1 > 1:
                metric_1 = 0
            else:
                metric_1 = max(100, - math.log(metric_1))

            total = metric_1 + metric_2

            player_result = [player_id, metric_1, metric_2, total]
            results.append(player_result)

        return results

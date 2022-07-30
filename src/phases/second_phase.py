"""The first phase of the buggypedia will contain a colaborative drawing contours game."""
import pathlib
from datetime import datetime, timedelta
from itertools import combinations
from random import randint
from time import mktime
from typing import Dict, List

import numpy as np
from fastapi import WebSocket
from PIL import Image

from phases.images import ImageManager


class SecondPhase:
    """Computes the logic of the first phase of the game."""

    submissions: Dict[WebSocket, List] = {}

    def __init__(self, players: dict[WebSocket:str], image_dir: pathlib.Path) -> None:
        """Instanciate a FirstPhase object from the number of players and images directory."""
        self.players = players
        self.image_dir = image_dir

    def start(self, difficulty: int) -> List[Dict]:
        """Start phase by sending image patches to everyone"""
        img = Image.open(self.image_dir)
        img_array = np.array(img)

        bug_locations = get_sphere_distribution(n=30)  # TODO: get this from the difficulty.

        locations_data = {}

        for id, bug in enumerate(bug_locations):
            start_dif = timedelta(3, randint(0, 15))
            start_time = datetime.now() + start_dif
            end_time = datetime.now() + start_dif + timedelta(0, randint(3, 10))

            locations_data[id] = {
                "x": bug[0],
                "y": bug[1],
                "start_time": mktime(start_time.timetuple()),
                "end_time": mktime(end_time.timetuple()),
            }

        return {
            "type": "phase_start",
            "data": {
                "phase": 2,
                "image": ImageManager.pillow_image_to_base64_string(Image.fromarray(img_array)),
                "locations": locations_data,
            },
        }

    def receive(self, websocket: WebSocket, data: dict):
        """Receive submissions from the frontend"""
        if data["data"].get("submission", None) is not None:
            self.submissions[websocket][1] = self.base64_string_to_pillow_image(data["data"]["submission"])
            metric = self.check_drawing_from_player(self.submissions[websocket][0], self.submissions[websocket][1])
            self.submissions[websocket][2] = metric

    @property
    def is_finished(self):
        """Check if everyoene has submitted"""
        for submission in self.submissions.values():
            if submission[2] is None:
                return False
        return True

    @property
    def metrics(self):
        """Get player data for the leaderboards"""
        return [metric[2] for metric in self.submissions.values()]

    def get_next_level_difficulty(self):
        """Query next level difficulty based on the metrics from the submissions"""
        return max(1, np.mean(self.metrics))


def get_sphere_distribution(n, sep=5):
    """Select n random points with min separation of :sep"""
    while True:
        P = np.random.rand(n, 2) * 100
        P = P.round(2)
        if all(np.linalg.norm(p - q) > sep for p, q in combinations(P, 2)):
            break
    return P

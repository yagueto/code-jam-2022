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

    locations_data = {}

    def __init__(self, players: dict[WebSocket:str], image_dir: pathlib.Path) -> None:
        """Instanciate a FirstPhase object from the number of players and images directory."""
        self.players = players
        self.image_dir = image_dir

    def start(self, difficulty: int) -> List[Dict]:
        """Start phase by sending image patches to everyone"""
        img = Image.open(self.image_dir)
        img_array = np.array(img)

        bug_locations = get_sphere_distribution(n=30)  # TODO: get this from the difficulty.

        for id, bug in enumerate(bug_locations):
            start_dif = timedelta(3, randint(0, 15))
            start_time = datetime.now() + start_dif
            end_time = datetime.now() + start_dif + timedelta(0, randint(3, 10))

            self.locations_data[id] = {
                "x": bug[0],
                "y": bug[1],
                "start_time": mktime(start_time.timetuple()),
                "end_time": mktime(end_time.timetuple()),
            }

        return {
            "type": "phase_start",
            "user": self.players.keys(),
            "data": {
                "phase": 2,
                "image": ImageManager.pillow_image_to_base64_string(Image.fromarray(img_array)),
                "locations": self.locations_data,
            },
        }

    def receive(self, websocket: WebSocket, data: dict):
        """Receive submissions from the frontend"""
        try:
            if data["data"].get("id", None) is not None:
                if True:
                    del self.locations_data[data["data"]["id"]]
                    return {
                        "type": "phase_update",
                        "user": self.players.keys(),
                        "data": {
                            "phase": 2,
                            "status": "remove",
                            "bug": data["data"]["id"],
                        },
                    }
        except KeyError:
            return {"user": websocket, "type": "phase_update", "data": {"phase": 2, "error": "bad request"}}

    @property
    def is_finished(self):
        """Check if everyoene has submitted"""
        if len(self.locations_data) == 0:
            return True

    @property
    def metrics(self):
        """Get player data for the leaderboards"""
        pass  # TODO

    def get_next_level_difficulty(self):
        """Query next level difficulty based on the metrics from the submissions"""
        return None


def get_sphere_distribution(n, sep=5):
    """Select n random points with min separation of :sep"""
    while True:
        P = np.random.rand(n, 2) * 100
        P = P.round(2)
        if all(np.linalg.norm(p - q) > sep for p, q in combinations(P, 2)):
            break
    return P

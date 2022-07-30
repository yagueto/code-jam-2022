"""The first phase of the buggypedia will contain a colaborative drawing contours game."""
import pathlib
import random
from typing import Dict, List

from fastapi import WebSocket
from numpy import mean
from PIL import Image

from .images import ImageManager

Patches = list[Image.Image]


class FirstPhase:
    """Computes the logic of the first phase of the game."""

    submissions: Dict[WebSocket, List] = {}

    def __init__(self, players: dict[WebSocket:str], images_dir: pathlib.Path) -> None:
        """Instanciate a FirstPhase object from the number of players and images directory."""
        self.players = players
        self.images_dir = images_dir

    def select_random_image(self) -> Image.Image:
        """Selects a random image that will be used in the game."""
        paths = [path for path in self.images_dir.iterdir() if path.suffix.lower() == ".png"]
        selected_path = random.choice(paths)
        image = Image.open(selected_path)
        image = ImageManager.convert_image_to_bit_format(image)
        return image

    def create_image_patches(self, image_to_split: Image.Image) -> Patches:
        """Divide the game image in different patches for different players"""
        patches = ImageManager.split_image(image_to_split, patches_number=len(self.players.keys()))

        return patches

    def check_drawing_from_player(self, original_patch: Image.Image, player_patch: Image.Image) -> float:
        """Checks how well each player has draw his part."""
        original_patch, player_patch = ImageManager.reshape_images(original_patch, player_patch)
        metric = ImageManager.compute_contour_similarity(player_patch, original_patch)

        return metric

    def start(self) -> List[Dict]:
        """Start phase by sending image patches to everyone"""
        patches = self.create_image_patches(self.select_random_image())
        events = []
        for i, player_socket in enumerate(self.players.keys()):
            b64img = ImageManager.pillow_image_to_base64_string(patches[i])
            self.submissions[player_socket] = [
                patches[i],
                None,
                None,
            ]  # patch, submission, metric
            events.append(
                {
                    "user": player_socket,
                    "type": "phase_start",
                    "data": {"image": b64img},
                }
            )
        return events

    def receive(self, websocket: WebSocket, data: dict):
        """Receive submissions from the frontend"""
        if data["data"].get("submission", None) is not None:
            self.submissions[websocket][1] = ImageManager.base64_string_to_pillow_image(data["data"]["submission"])
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
        return {player_socket: metric[2] for player_socket, metric in self.submissions.items()}

    def get_next_level_difficulty(self):
        """Query next level difficulty based on the metrics from the submissions"""
        return max(1, mean(list(self.metrics.values())))

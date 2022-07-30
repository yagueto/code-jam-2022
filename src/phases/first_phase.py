"""The first phase of the buggypedia will contain a colaborative drawing contours game."""
import pathlib
import random
from base64 import b64encode, decodebytes
from io import BytesIO
from typing import Dict, List

from fastapi import WebSocket
from PIL import Image

from .images import ImageManager

Patches = list[Image.Image]


class FirstPhase:
    """Computes the logic of the first phase of the game."""

    submissions: Dict[WebSocket, List] = {}

    def __init__(self, players: int, images_dir: pathlib.Path) -> None:
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

    def check_drawing_from_player(self, original_patch: Image, player_patch: Image) -> list[float]:
        """Checks how well each player has draw his part."""
        original_patch, player_patch = ImageManager.reshape_images(original_patch, player_patch)
        metric = ImageManager.compute_contour_similarity(player_patch, original_patch)

        return metric

    def pillow_image_to_base64_string(self, img):
        """Convert PIL image to base64 to send through websocket"""
        buffered = BytesIO()
        img.save(buffered, format="JPEG")
        return b64encode(buffered.getvalue()).decode("utf-8")

    def base64_string_to_pillow_image(self, base64_str):
        """Convert received base64 str to PIL image"""
        return Image.open(BytesIO(decodebytes(bytes(base64_str, "utf-8"))))

    def start(self) -> List[Dict]:
        """Start phase by sending image patches to everyone"""
        patches = self.create_image_patches(self.select_random_image())
        events = []
        for i in range(0, len(self.players)):
            b64img = self.pillow_image_to_base64_string(patches[i])
            self.submissions[list(self.players.keys())[i]] = [patches[i], None, None]
            events.append(
                {
                    "user": list(self.players.keys())[i],
                    "type": "phase_start",
                    "data": {"image": b64img},
                }
            )
        return events

    def receive(self, websocket, data):  # noqa: D102
        if data["data"].get("submission", None) is not None:
            self.submissions[websocket][1] = self.base64_string_to_pillow_image(data["data"]["submission"])
            print(self.check_drawing_from_player(self.submissions[websocket][0], self.submissions[websocket][1]))

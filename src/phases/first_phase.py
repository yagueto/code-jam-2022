"""The first phase of the buggypedia will contain a colaborative drawing contours game."""
import pathlib
import random

from PIL import Image

from ..images import ImageManager

Patches = list[Image.Image]


class FirstPhase:
    """Computes the logic of the first phase of the game."""

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
        patches = ImageManager.split_image(image_to_split, patches_number=self.players)
        return patches

    def check_drawings_from_players(self, original_patchs: Patches, player_patchs: Patches) -> list[float]:
        """Checks how well each player has draw his part."""
        metrics = []
        for original_patch, player_patch in zip(original_patchs, player_patchs):
            original_patch, player_patch = ImageManager.reshape_images(original_patch, player_patch)
            metric = ImageManager.compute_contour_similarity(player_patch, original_patch)
            metrics.append(metric)

        return metrics

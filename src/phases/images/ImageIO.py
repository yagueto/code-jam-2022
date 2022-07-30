import io
from typing import Protocol

from PIL import Image


class ImageTransmisionProtocol(Protocol):
    """Protocol for the image transmision."""

    def process_received_image(self, byte_strem: io.BytesIO) -> Image.Image:
        """Convert the bytes stream into a PIL image."""
        ...

    def prepare_image_to_send(self, image: Image.Image) -> io.BytesIO:
        """Transform image to a byte stream."""
        ...

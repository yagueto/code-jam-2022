import io
from typing import Protocol

from PIL import Image


class ImageProtocol(Protocol):
    """Protocol for the image processing."""

    def compute_image_similarity(self, fake_image: Image.Image, original_image: Image.Image) -> float:
        """Compares the images using a image similarity algorithm and returns a float between 0 and 1."""
        ...

    def split_image(self, image: Image.Image, patches_number: int = 4) -> tuple[Image.Image, ...]:
        """
        Split the image in the number of specified images.

        If the number of images are odd, the last image double in size to the others.
        """
        ...

    def adapt_image_size(self, image_to_adapt: Image.Image, reference_image: Image.Image) -> Image.Image:
        """Changes the dimensions of an image to match the dimensions of the specified image."""
        ...


class ImageTransmisionProtocol(Protocol):
    """Protocol for the image transmision."""

    def process_received_image(self, byte_strem: io.BytesIO) -> Image.Image:
        """Convert the bytes stream into a PIL image."""
        ...

    def prepare_image_to_send(self, image: Image.Image) -> io.BytesIO:
        """Transform image to a byte stream."""
        ...


def main():  # noqa: D103
    pass


if __name__ == "__main__":
    main()

from typing import Protocol

import cv2
from PIL import Image

from . import ImageExceptions


class ImageProtocol(Protocol):
    """Protocol for the image processing."""

    def compute_contour_similarity(fake_contour: Image.Image, original_contour: Image.Image) -> float:
        """Compares the contour using a image similarity algorithm and returns a float between 0 and 1."""
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


def convert_image_to_bit_format(image: Image.Image) -> Image:
    """Convert PIL Image to bit mode."""
    return image.convert(mode="1")


def compute_contour_similarity(fake_contour: Image.Image, original_contour: Image.Image) -> float:
    """Compares the contour using a image similarity algorithm and returns a float between 0 and 1."""
    if fake_contour.mode == "1":
        raise ImageExceptions.ImageFormatNotSupported(fake_contour)
    elif original_contour.mode == "1":
        raise ImageExceptions.ImageFormatNotSupported(original_contour)

    similarity = cv2.matchShapes(fake_contour, original_contour)

    return similarity


def main():  # noqa: D103
    print(Image)


if __name__ == "__main__":
    main()

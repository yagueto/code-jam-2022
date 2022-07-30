from typing import Protocol

import cv2
import numpy as np
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


def split_image(image: Image.Image, patches_number: int = 4) -> list[Image.Image]:
    """
    Split the image in the number of specified images.

    If the number of images are odd, the last image double in size to the others.
    """
    if patches_number <= 0:
        raise ImageExceptions.IncompatiblePatchNumber("Patches must be grater than 0.")

    if patches_number == 1:
        return (image,)

    mode = image.mode
    size = image.size
    odd_patches = (patches_number % 2 != 0)
    total_cols = 2

    if odd_patches:
        total_rows = (patches_number // 2) + 1
    else:
        total_rows = patches_number // 2

    new_size = (size[0] // total_rows, size[1] // total_cols)

    patches = []
    image = np.array(image)

    for i in range(patches_number):
        col = (i % 2)
        row = (i // 2)

        if i + 1 == patches_number and odd_patches:
            patch = image[:, new_size[0] * row: new_size[0] * (row + 1)]
        elif col == 1:
            patch = image[new_size[1] * col:, new_size[0] * row: new_size[0] * (row + 1)]
        else:
            patch = image[new_size[1] * col: new_size[1] * (col + 1), new_size[0] * row: new_size[0] * (row + 1)]

        patch = Image.fromarray(patch, mode)
        patches.append(patch)

    return patches


def convert_image_to_bit_format(image: Image.Image) -> Image.Image:
    """Convert PIL Image to bit mode."""
    return image.convert(mode="L")


def reshape_images(image_1: Image.Image, image_2: Image.Image) -> tuple[Image.Image, Image.Image]:
    """Resize image_2 to match image_1 shape."""
    shape = image_1.size
    image_2 = image_2.resize(shape)
    return image_1, image_2


def compute_contour_similarity(fake_contour: Image.Image, original_contour: Image.Image) -> float:
    """Compares the contour using a image similarity algorithm and returns a float between 0 and 1."""
    if fake_contour.mode != "L":
        raise ImageExceptions.ImageFormatNotSupported(fake_contour)
    elif original_contour.mode != "L":
        raise ImageExceptions.ImageFormatNotSupported(original_contour)

    fake_array = np.array(fake_contour).astype(np.float32)
    original_array = np.array(original_contour).astype(np.float32)

    similarity = cv2.matchShapes(fake_array, original_array, 1, 0.0)

    return similarity


def main():  # noqa: D103
    print(Image)


if __name__ == "__main__":
    main()

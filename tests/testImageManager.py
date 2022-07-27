import pathlib
import unittest

from PIL import Image

from src.images import ImageExceptions, ImageManager


class TestImageManager(unittest.TestCase):
    """Creates the setup for testing ImageManager by opening test images."""

    IMAGES_DIR = pathlib.Path("tests/misc")

    def setUp(self) -> None:
        """Load images before running tests."""
        fake_path = TestImageManager.IMAGES_DIR / "fake.png"
        original_path = TestImageManager.IMAGES_DIR / "original.png"
        self.fake_img = Image.open(fake_path)
        self.original_img = Image.open(original_path)


class TestConvertImageToBitformat(TestImageManager):
    """Test the convert_image_to_bitformat method."""

    def test_convert_image_to_bitformat(self):
        """Checks that the final PIL mode is '1'."""
        converted_img = ImageManager.convert_image_to_bit_format(self.fake_img)
        self.assertEqual(converted_img.mode, "1")


class TestComputeContourSimilarity(TestImageManager):
    """Test the compute_contour_similarity method."""

    def test_similarity(self):
        """Checks if the method is able to return a float greater than 0."""
        fake_img = ImageManager.convert_image_to_bit_format(self.fake_img)
        original_img = ImageManager.convert_image_to_bit_format(self.original_img)
        original_img, fake_img = ImageManager.reshape_images(original_img, fake_img)
        similarity = ImageManager.compute_contour_similarity(fake_img, original_img)
        self.assertGreaterEqual(similarity, 0)

    def test_wrong_format(self):
        """Checks that the method raises an error when the PIL mode is different from '1'."""
        with self.assertRaises(ImageExceptions.ImageFormatNotSupported):
            ImageManager.compute_contour_similarity(self.fake_img, self.original_img)


class TestReshapeImages(TestImageManager):
    """Checks the reshape_images method."""

    def test_shapes_matches(self):
        """Checks if the images have the same sizes after the method."""
        original_img, fake_img = ImageManager.reshape_images(self.original_img, self.fake_img)
        self.assertTupleEqual(original_img.size, fake_img.size)

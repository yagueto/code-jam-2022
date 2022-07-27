from PIL import Image

class ImageFormatNotSupported(Exception):

    def __init__(self, image: Image.Image, message: str = "Image format is not supported") -> None:
        self.image = image
        self.message = message
        super().__init__(f"{message} -> IMAGE FORMAT: {self.image.mode}")
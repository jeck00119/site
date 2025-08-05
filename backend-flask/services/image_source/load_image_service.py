import base64
import io

import cv2
import numpy as np
from PIL import Image

from src.metaclasses.singleton import Singleton


class LoadImageService(metaclass=Singleton):
    def __init__(self):
        self.frame = None
        self.image_encoded = None

    def set_encoded_image(self, image_encoded: str):
        self.image_encoded = image_encoded

    def load_image(self):
        if self.image_encoded is not None:
            decoded = base64.b64decode(self.image_encoded[self.image_encoded.find(',') + 1:])
            image = Image.open(io.BytesIO(decoded))
            self.frame = cv2.cvtColor(np.array(image), cv2.COLOR_RGB2BGR)
        else:
            self.frame = None

    def get_frame(self):
        return self.frame

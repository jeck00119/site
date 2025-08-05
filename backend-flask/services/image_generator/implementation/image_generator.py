from os import listdir
from os.path import join, isfile

import cv2
import numpy as np

from services.image_generator.img_generator_model import ImageGeneratorModel


class ImageGenerator():
    def __init__(self, img_data_model:ImageGeneratorModel):
        self.dir_path = img_data_model.dir_path

        self.currentFrameIndex = 0
        self.frames = []

        try:
            files = [f for f in listdir(self.dir_path) if isfile(join(self.dir_path, f))]

            for file in files:
                if file.endswith(".png") or file.endswith(".jpg") or file.endswith(".jpeg") or file.endswith('.bmp'):
                    path = f"{self.dir_path}/{file}"
                    img = cv2.imread(path)
                    self.frames.append(img)
        except FileNotFoundError:
            error_frame = np.zeros(shape=(640, 700, 3), dtype=np.uint8)
            cv2.putText(error_frame, "SELECTED DIRECTORY", (0, 320), cv2.FONT_HERSHEY_DUPLEX, 2,
                        (0, 0, 255), 3)
            cv2.putText(error_frame, "DOES NOT EXIST", (0, 480), cv2.FONT_HERSHEY_DUPLEX, 2, (0, 0, 255), 3)
            self.frames.append(error_frame)

    def get_frame(self):
        frame = self.frames[self.currentFrameIndex]

        if self.currentFrameIndex == len(self.frames) - 1:
            self.currentFrameIndex = 0
        else:
            self.currentFrameIndex += 1

        return frame

    def change_directory(self, directory_path: str):
        self.dir_path = directory_path

        self.currentFrameIndex = 0
        self.frames = []

        files = [f for f in listdir(self.dir_path) if isfile(join(self.dir_path, f))]

        for file in files:
            if file.endswith(".png") or file.endswith(".jpg") or file.endswith(".jpeg"):
                path = f"{self.dir_path}/{file}"
                img = cv2.imread(path)
                self.frames.append(img)


from services.image_source.image_source_service import ImageSourceService
from services.image_source.load_image_service import LoadImageService
from src.metaclasses.singleton import Singleton
from src.utils import crop_roi


class MasksService(metaclass=Singleton):
    def __init__(self, image_source_service: ImageSourceService, load_image_service: LoadImageService):
        self.image_source_service = image_source_service
        self.load_image_service = load_image_service

    def extract_roi(self, image_source_uid, graphics, image_source=True):
        if image_source:
            frame = self.image_source_service.grab_from_image_source(image_source_uid)
        else:
            frame = self.load_image_service.get_frame()

        roi, _ = crop_roi(frame, graphics["offset"], graphics["bound"],
                          graphics["rect"], graphics["rotation"])

        return roi

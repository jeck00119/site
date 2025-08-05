import cv2
import numpy

from repo.repositories import ImageSourceRepository, CameraCalibrationRepository
from repo.repository_exceptions import UidNotFound
from services.camera.camera_service import CameraService
from services.image_generator.image_generator_service import ImageGeneratorService
from services.image_source.image_source_model import ImageSourceModel, ImgSrcEnum
from src.metaclasses.singleton import Singleton


class ImageSourceService(metaclass=Singleton):
    def __init__(self):
        self.image_sources: dict[str, ImageSourceModel] = {}
        self.live_image_source : ImageSourceModel = None
        self.images_sources_last_frame : dict[str, numpy.ndarray] = {}
        self.image_sources_repository:ImageSourceRepository = ImageSourceRepository()
        self.camera_calibration_repository: CameraCalibrationRepository = CameraCalibrationRepository()

        self.camera_service = CameraService()
        self.image_generator_service = ImageGeneratorService()

    def initialize_all_image_sources(self):
        for img_src in self.image_sources_repository.read_all():
            try:
                self._initialize_image_source_by_uid(img_src['uid'])
            except:
                pass

    def grab_from_image_source(self, uid):
        image = cv2.imread('assets/no_camera.jpg')
        self.images_sources_last_frame[uid] = image

        if uid in self.image_sources.keys():
            if self.image_sources[uid].image_source_type == ImgSrcEnum.DYNAMIC:
                image = self.camera_service.grab_from_camera(self.image_sources[uid].camera_uid)
            elif self.image_sources[uid].image_source_type == ImgSrcEnum.STATIC:
                image = self.image_generator_service.grab_from_generator(self.image_sources[uid].image_generator_uid)

            self.images_sources_last_frame[uid] = image

        return image

    def get_frame(self, uid):
        if uid not in self.images_sources_last_frame.keys():
            raise UidNotFound

        return self.images_sources_last_frame[uid]

    def on_patch_image_source(self, image_source: ImageSourceModel):
        self._uninitialize_image_source_by_uid(image_source.uid)
        self._initialize_image_source_by_uid(image_source.uid)

    def on_delete_image_source(self, image_source_id):
        self._uninitialize_image_source_by_uid(image_source_id)

    def _initialize_image_source_by_uid(self, uid):
        if uid not in self.image_sources.keys():
            image_source_model = ImageSourceModel(**self.image_sources_repository.read_id(uid))

            if image_source_model.image_source_type == ImgSrcEnum.DYNAMIC:
                if image_source_model.camera_uid != '':
                    self.camera_service.initialize_camera(image_source_model.camera_uid)
                    self.camera_service.load_setting_file(image_source_model.camera_uid,
                                                          image_source_model.camera_settings_uid)
                self.image_sources[uid] = image_source_model

            elif image_source_model.image_source_type == ImgSrcEnum.STATIC:
                if image_source_model.image_generator_uid != '':
                    self.image_generator_service.initialize_generator(image_source_model.image_generator_uid)
                self.image_sources[uid] = image_source_model
        else:
            return ' '

    def _uninitialize_image_source_by_uid(self, uid):
        if uid not in self.image_sources.keys():
           return
        else:
            if self.image_sources[uid].image_source_type == ImgSrcEnum.DYNAMIC:
               # self.camera_service.release_camera(self.image_sources[uid].camera_uid)
               self.image_sources.pop(uid)
            elif self.image_sources[uid].image_source_type == ImgSrcEnum.STATIC:
                self.image_sources.pop(uid)

    def load_settings_to_image_source(self, uid):
        settings_uid = self.image_sources[uid].camera_settings_uid
        camera_uid = self.image_sources[uid].camera_uid

        self.camera_service.load_setting_file(camera_uid, settings_uid)

    def check_image_source_type(self, uid):
        image_source_model = ImageSourceModel(**self.image_sources_repository.read_id(uid))

        if image_source_model.image_source_type == ImgSrcEnum.DYNAMIC:
            return image_source_model.image_source_type

        elif image_source_model.image_source_type == ImgSrcEnum.STATIC:
            return image_source_model.image_source_type

    def get_calibration_uid(self, uid):
        if uid in self.image_sources.keys():
            return self.image_sources.get(uid).camera_calibration_uid
        return None

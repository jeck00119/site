import cv2

from repo.repositories import CameraSettingsRepository, CameraRepository
from repo.repository_exceptions import UidNotFound
from services.camera.camera_factory import CameraFactory
from services.camera.camera_model import CameraModel, EnumCameraTypes, WebCamSettingsModel, BaslerSettingsModel
from services.camera.implementation.basler_camera import BaslerCamera
from services.camera.implementation.interface_camera import CameraInterface
from src.metaclasses.singleton import Singleton


class CameraService(metaclass=Singleton):
    def __init__(self):
        self._is_initialized = False

        self.cameras: dict[str, CameraInterface] = {}
        self.camera_repository = CameraRepository()
        self.camera_settings_repository = CameraSettingsRepository()

    def initialize_all_cameras(self):
        for cam_doc in self.camera_repository.read_all():
            self.initialize_camera(cam_doc['uid'])

    def find_basler_cameras(self):
        return BaslerCamera.find_cameras()

    def initialize_camera(self, uid):
        if uid not in self.cameras.keys():
            cam_doc = self.camera_repository.read_id(uid)
            if cam_doc:
                camera = CameraFactory.create_camera(CameraModel(**cam_doc))
                res = camera.initialize()
                self.cameras[uid] = camera
                return res
            else:
                return f'Camera with id: {uid} cannot be found in db.'

    def release_camera(self, uid):
        if uid in self.cameras.keys():
            self.cameras[uid].release()
            self.cameras.pop(uid)
            return f'Camera with id:{uid} has been released'
        else:
            return f'Camera with id:{uid} is not initialized.'

    def patch_camera(self, camera_model: CameraModel):
        self.release_camera(camera_model.uid)
        self.initialize_camera(camera_model.uid)

    def post_camera(self, camera_model: CameraModel):
        self.initialize_camera(camera_model.uid)

    def delete_camera(self, camera_uid):
        self.release_camera(camera_uid)

    def load_setting_file(self, uid, camera_setting_uid):
        if uid in self.cameras.keys():
            try:
                camera_settings = self.camera_settings_repository.read_id(camera_setting_uid)
                if self.cameras[uid].type == EnumCameraTypes.basler_usb:
                    camera_settings = BaslerSettingsModel(**camera_settings)
                else:
                    camera_settings = WebCamSettingsModel(**camera_settings)

                if camera_settings:
                    self.cameras[uid].load_config(camera_settings.model_dump())
                return f'Camera settings {camera_setting_uid} loaded.'
            except UidNotFound:
                pass
        else:
            return f'Camera with id {uid} dosent exist/is not initialized.'

    def load_settings_from_dict(self, camera_uid, settings):
        self.cameras[camera_uid].load_config(settings)

    def change_camera_prop(self, uid, name, value):
        if uid in self.cameras.keys():
            self.cameras[uid].set(name, value)
        else:
            return f'Camera with id {uid} dosent exist/is not initialized.'

    def grab_from_camera(self, uid):
        if uid not in self.cameras.keys():
            image = cv2.imread('assets/no_camera.jpg')
            return image

        if self.cameras[uid].type == EnumCameraTypes.basler_usb:
            frame = self.cameras[uid].get_frame()
            return frame

        if self.cameras[uid].type == EnumCameraTypes.webcam_logi or self.cameras[uid].type == EnumCameraTypes.webcam_msft:
            if not self.cameras[uid]._cap.isOpened():
                image = cv2.imread('assets/cap_not_opened.jpg')
                return image

            frame = self.cameras[uid].get_frame()
            return frame

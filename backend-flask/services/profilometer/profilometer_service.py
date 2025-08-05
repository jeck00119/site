from repo.repositories import ProfilometerRepository
from services.profilometer.profilometer_builder import ProfilometerBuilder
from src.metaclasses.singleton import Singleton
import logging


class ProfilometerService(metaclass=Singleton):
    def __init__(self, offline: bool = False):
        super(ProfilometerService, self).__init__()
        self.logger = logging.getLogger(__name__)
        self._profilometer_repo = ProfilometerRepository()
        self.offline = offline
        self.profilometers = {}

    @staticmethod
    def get_available_types():
        return ["LMI"]

    def start_profilometer_service(self):
        profilometer_models = self._profilometer_repo.read_all()

        if len(profilometer_models) == 0:
            profilometer = ProfilometerBuilder.create_profilometer(profilometer_type="LMIDummy")
            profilometer.start()
            mock_id = generate_uid()
            self.profilometers[mock_id] = profilometer
        else:
            for profilometer_model in profilometer_models:
                if self.offline:
                    profilometer = ProfilometerBuilder.create_profilometer(profilometer_type="LMIDummy")
                    profilometer.start()
                    mock_id = generate_uid()
                    self.profilometers[mock_id] = profilometer
                else:
                    try:
                        self._init_profilometer_from_dict(profilometer_model)
                    except Exception as e:
                        self.logger.error(repr(e))

    def update_profilometers(self, profilometer_models: list):
        saved_profilometers = self._profilometer_repo.read_all()

        found_profilometers = {}

        for profilometer in saved_profilometers:
            found_profilometers[profilometer["uid"]] = False

        saved_uids = list(found_profilometers.keys())

        update = []
        delete = []
        add = []

        for profilometer_model in profilometer_models:
            if profilometer_model.uid in saved_uids:
                found_profilometers[profilometer_model.uid] = True

                if profilometer_model.id != self.profilometers[profilometer_model.id].get_id():
                    self._release_profilometer(profilometer_model.uid)
                    self._init_profilometer_from_dict(profilometer_model.__dict__)
                    update.append(profilometer_model.uid)
                # continue
            else:
                if self.offline:
                    profilometer = ProfilometerBuilder.create_profilometer(profilometer_type="LMIDummy")
                    profilometer.start()
                    mock_id = generate_uid()
                    self.profilometers[mock_id] = profilometer
                else:
                    self._init_profilometer_from_dict(profilometer_model.__dict__)
                    add.append(profilometer_model.uid)

        for profilometer_uid, found in found_profilometers.items():
            if not found:
                self.profilometers[profilometer_uid].release_resources()
                delete.append(profilometer_uid)

        return add, update, delete

    def _init_profilometer_from_dict(self, profilometer_dict):
        profilometer_dict["configPath"] = ""
        profilometer = ProfilometerBuilder.create_profilometer(profilometer_type=profilometer_dict["type"],
                                                               data=profilometer_dict)
        if profilometer:
            profilometer.start()
            self.profilometers[profilometer_dict["uid"]] = profilometer

    def _release_profilometer(self, uid):
        self.profilometers[uid].release_resources()
        self.profilometers.pop(uid)

    def un_initialize(self):
        for profilometers in self.profilometers.values():
            profilometers.release_resources()

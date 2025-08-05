from services.profilometer.dependencies.gocator_client import GocatorClient, GocatorClientDummy


class ProfilometerBuilder:
    LMI = "LMI"
    LMI_DUMMY = "LMIDummy"

    @staticmethod
    def create_profilometer(profilometer_type: str, data: [None, dict] = None):
        if profilometer_type in ProfilometerBuilder.LMI:
            return GocatorClient(serial_numbers=data["id"], config_path=data["configPath"],
                                 server_file_path=data["path"])
        elif profilometer_type in ProfilometerBuilder.LMI_DUMMY:
            return GocatorClientDummy()
        else:
            return None

import logging
from services.profilometer.dependencies.gocator_client import GocatorClient, GocatorClientDummy


class ProfilometerBuilder:
    LMI = "LMI"
    LMI_DUMMY = "LMIDummy"
    # Note: Keyence and SICK profilometers would be added here with their builders

    @staticmethod
    def create_profilometer(profilometer_type: str, data: [None, dict] = None):
        """
        Create profilometer with validation.
        
        Note: Different profilometer types use different connection methods:
        - Gocator (LMI): Network connection (IP + port) - no USB validation needed
        - Keyence: May use serial/USB connection - would need USB validation
        - SICK: May use serial/USB connection - would need USB validation
        """
        logger = logging.getLogger(__name__)
        
        try:
            if profilometer_type in ProfilometerBuilder.LMI:
                # Gocator uses network connection, no USB port validation needed
                logger.info(f"Creating Gocator profilometer with network connection")
                return GocatorClient(serial_numbers=data["id"], config_path=data["configPath"],
                                     server_file_path=data["path"])
            elif profilometer_type in ProfilometerBuilder.LMI_DUMMY:
                return GocatorClientDummy()
            else:
                logger.error(f"Unknown profilometer type: {profilometer_type}")
                return None
                
        except Exception as e:
            logger.error(f"Failed to create profilometer: {e}")
            return None
    
    @staticmethod
    def validate_profilometer_connection(profilometer_model):
        """
        Validate profilometer connection based on type.
        
        For future implementation when adding Keyence/SICK profilometers:
        - Check if they use serial ports and validate with UnifiedUSBManager
        - Network-based profilometers (like Gocator) would use network validation
        """
        # This would be implemented when adding serial-based profilometers
        # For now, Gocator uses network connections so no USB validation needed
        return True

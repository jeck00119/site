# Import error lists from existing files
from services.cnc.cnc_machine_marlin import ERROR_LIST_CNC as MARLIN_ERROR_LIST
from services.cnc.cnc_machine_gerbil import ERROR_LIST_CNC as GRBL_ERROR_LIST


class CncErrorHandler:
    """Centralized error handling for all CNC firmware types"""
    
    ERROR_LISTS = {
        'Marlin': MARLIN_ERROR_LIST,
        'GRBL': GRBL_ERROR_LIST,
        'FluidNC': GRBL_ERROR_LIST  # FluidNC uses GRBL error codes
    }
    
    @staticmethod
    def get_error_message(firmware_type: str, error_code: str) -> str:
        """Get human-readable error message for firmware error code"""
        error_list = CncErrorHandler.ERROR_LISTS.get(firmware_type, GRBL_ERROR_LIST)
        return error_list.get(error_code, error_code)
    
    @staticmethod
    def format_error_for_callback(firmware_type: str, error_data) -> dict:
        """Format error data for callback system"""
        if isinstance(error_data, tuple) and len(error_data) >= 2:
            error_code = error_data[1]
        else:
            error_code = str(error_data)
        
        error_message = CncErrorHandler.get_error_message(firmware_type, error_code)
        return {
            'event': 'on_error',
            'message': error_message,
            'error_code': error_code,
            'firmware_type': firmware_type
        }
    
    @staticmethod
    def get_supported_firmware_types() -> list:
        """Get list of supported firmware types"""
        return list(CncErrorHandler.ERROR_LISTS.keys())
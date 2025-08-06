import os
import shutil
from src.platform_utils import is_windows, is_linux

def get_tesseract_installation_dir():
    """Get cross-platform Tesseract installation directory"""
    if is_windows():
        # Try common Windows installation paths
        common_paths = [
            'C:/Program Files/Tesseract-OCR',
            'C:/Program Files (x86)/Tesseract-OCR',
            os.path.expanduser('~/AppData/Local/Tesseract-OCR')
        ]
        for path in common_paths:
            if os.path.exists(path):
                return path
    elif is_linux():
        # Try to find tesseract in system PATH first
        tesseract_path = shutil.which('tesseract')
        if tesseract_path:
            return os.path.dirname(tesseract_path)
        
        # Check common Linux installation locations
        common_paths = ['/usr/bin', '/usr/local/bin', '/opt/tesseract/bin']
        for path in common_paths:
            if os.path.exists(os.path.join(path, 'tesseract')):
                return path
    
    # Fallback: try to find in system PATH
    tesseract_path = shutil.which('tesseract')
    if tesseract_path:
        return os.path.dirname(tesseract_path)
    
    # Final fallback for Windows
    if is_windows():
        return 'C:/Program Files/Tesseract-OCR'
    
    # Final fallback for Linux
    return '/usr/bin'

TESSERACT_INSTALLATION_DIR = get_tesseract_installation_dir()
DEBUG_FOLDER_PATH = "debug_img"

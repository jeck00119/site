import os
from src.platform_utils import PathHandler, PlatformSpecificConfig

# Initialize platform-specific environment
PlatformSpecificConfig.setup_environment()

# Environment configuration for data paths - cross-platform compatible
COGNEX_DATA_PATH = PathHandler.join_paths(PathHandler.get_data_directory(), "cognex", "DMC.csv")

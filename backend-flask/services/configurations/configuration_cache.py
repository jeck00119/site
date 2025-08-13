"""
Configuration Caching Layer for AOI Platform

Provides fast, atomic configuration switching with clean state isolation.
Ensures no cross-contamination between configurations while dramatically 
improving switch performance.
"""

import os
import json
import time
from pathlib import Path
from typing import Dict, Any, Optional
from threading import Lock

from src.metaclasses.singleton import Singleton


class ConfigurationCache(metaclass=Singleton):
    """
    Thread-safe configuration caching layer.
    
    Caches all configuration files in memory for fast switching while
    maintaining clean state isolation between configurations.
    """
    
    def __init__(self):
        self._cache: Dict[str, Dict[str, Any]] = {}
        self._cache_timestamps: Dict[str, float] = {}
        self._lock = Lock()
        self._config_db_path = self._get_config_db_path()
        
        # Configuration file mappings
        self._config_files = [
            'algorithms.json',
            'cameras.json', 
            'camera_settings.json',
            'cnc.json',
            'components.json',
            'identifications.json',
            'custom_components.json',
            'image_generator.json',
            'image_source.json',
            'inspections.json',
            'locations.json',
            'profilometer.json',
            'references.json',
            'robot.json',
            'audio_events.json',
            'camera_calibration.json',
            'stereo_calibration.json',
            'robot_positions.json'
        ]
    
    def _get_config_db_path(self) -> Path:
        """Get the configuration database path."""
        current_file = Path(__file__)
        return current_file.parent.parent.parent / "config_db"
    
    def _load_configuration_from_disk(self, config_name: str) -> Dict[str, Any]:
        """
        Load all configuration files for a given configuration from disk.
        
        Returns a dictionary with file names as keys and their contents as values.
        Missing or empty files are handled gracefully.
        """
        config_path = self._config_db_path / config_name
        config_data = {}
        
        if not config_path.exists():
            raise FileNotFoundError(f"Configuration '{config_name}' not found at {config_path}")
        
        for file_name in self._config_files:
            file_path = config_path / file_name
            
            try:
                if file_path.exists() and file_path.stat().st_size > 0:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        config_data[file_name] = json.load(f)
                else:
                    # Empty or missing file - initialize with empty structure
                    config_data[file_name] = {}
                    
            except (json.JSONDecodeError, IOError) as e:
                print(f"Warning: Failed to load {file_path}: {e}")
                config_data[file_name] = {}
        
        return config_data
    
    def _is_cache_stale(self, config_name: str) -> bool:
        """Check if cached configuration is stale by comparing file timestamps."""
        if config_name not in self._cache_timestamps:
            return True
            
        cached_time = self._cache_timestamps[config_name]
        config_path = self._config_db_path / config_name
        
        if not config_path.exists():
            return True
            
        # Check if any config file is newer than cache
        for file_name in self._config_files:
            file_path = config_path / file_name
            if file_path.exists():
                file_time = file_path.stat().st_mtime
                if file_time > cached_time:
                    return True
        
        return False
    
    def get_configuration(self, config_name: str, force_reload: bool = False) -> Dict[str, Any]:
        """
        Get configuration data, using cache when possible.
        
        Args:
            config_name: Name of the configuration to load
            force_reload: If True, bypass cache and reload from disk
            
        Returns:
            Dictionary containing all configuration file data
        """
        with self._lock:
            # Check cache validity
            if not force_reload and config_name in self._cache:
                if not self._is_cache_stale(config_name):
                    print(f"[CONFIG-CACHE] Using cached data for '{config_name}'")
                    return self._cache[config_name]
            
            # Load from disk and cache
            print(f"[CONFIG-CACHE] Loading '{config_name}' from disk")
            config_data = self._load_configuration_from_disk(config_name)
            
            # Update cache
            self._cache[config_name] = config_data
            self._cache_timestamps[config_name] = time.time()
            
            return config_data
    
    def preload_configurations(self, config_names: list[str]) -> None:
        """Preload multiple configurations into cache."""
        print(f"[CONFIG-CACHE] Preloading {len(config_names)} configurations")
        
        for config_name in config_names:
            try:
                self.get_configuration(config_name)
            except Exception as e:
                print(f"[CONFIG-CACHE] Failed to preload '{config_name}': {e}")
    
    def invalidate_configuration(self, config_name: str) -> None:
        """Remove configuration from cache, forcing next access to reload from disk."""
        with self._lock:
            if config_name in self._cache:
                del self._cache[config_name]
                del self._cache_timestamps[config_name]
                print(f"[CONFIG-CACHE] Invalidated cache for '{config_name}'")
    
    def clear_cache(self) -> None:
        """Clear entire cache."""
        with self._lock:
            self._cache.clear()
            self._cache_timestamps.clear()
            print("[CONFIG-CACHE] Cache cleared")
    
    def get_cache_stats(self) -> Dict[str, Any]:
        """Get cache statistics for monitoring."""
        with self._lock:
            return {
                'cached_configurations': len(self._cache),
                'configurations': list(self._cache.keys()),
                'total_cache_size_mb': self._estimate_cache_size_mb()
            }
    
    def _estimate_cache_size_mb(self) -> float:
        """Rough estimate of cache memory usage."""
        import sys
        total_size = 0
        for config_data in self._cache.values():
            total_size += sys.getsizeof(str(config_data))
        return total_size / (1024 * 1024)
    
    def warm_cache_with_common_configs(self) -> None:
        """Preload most commonly used configurations."""
        # Get list of available configurations
        if not self._config_db_path.exists():
            return
            
        common_configs = []
        for item in self._config_db_path.iterdir():
            if item.is_dir() and item.name.startswith('IBS-'):
                common_configs.append(item.name)
        
        # Preload all configurations for faster switching
        if common_configs:
            self.preload_configurations(common_configs)
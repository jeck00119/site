import os
import queue
import shutil
import time
import threading
from datetime import datetime

import pygame

from services.media.media import Media
from src.metaclasses.singleton import Singleton
from services.logger.logger_model import AppEntry


class PygameMediaService(metaclass=Singleton):
    def __init__(self):
        self.app_logger = None  # Will be set after ServiceManager initializes
        
        try:
            pygame.mixer.init()
            print(" Pygame mixer initialized successfully")
        except pygame.error as e:
            error_msg = f"Failed to initialize pygame mixer: {e}"
            print(f" {error_msg}")
            raise RuntimeError(f"Audio system initialization failed: {e}")
            
        self.repository = None
        self.sound_path = ''
        self.channels = []
        self.channel_sounds = []
        self.channel_states = []
        self.channel_volumes = []
        self.channel_positions = []
        self.channel_loops = []

        self.priorityQueue = queue.PriorityQueue()

        try:
            self.create_repository()
        except Exception as e:
            print(f" Failed to create audio repository: {e}")
            raise
    
    def _log_event(self, event_type: str, title: str, description: str, details: str = ""):
        """Log events using the existing AppLogger service"""
        try:
            if self.app_logger is None:
                # Get logger from ServiceManager after it's initialized
                from services.service_manager import ServiceManager
                self.app_logger = ServiceManager.app_log
            
            if self.app_logger:
                entry = AppEntry(
                    timestamp=datetime.now().isoformat(),
                    user="audio_service",
                    type=event_type,
                    title=title,
                    description=description,
                    details=details
                )
                self.app_logger.add(entry)
        except Exception:
            # Fallback to console if logging fails
            print(f"[{event_type}] {title}: {description}")

    def create_repository(self):
        pass

    def init_sound_path(self):
        pass

    def get_media_list(self):
        try:
            if not self.sound_path or not os.path.exists(self.sound_path):
                self._log_event("WARNING", "Sound Path Issue", f"Sound path not configured or doesn't exist: {self.sound_path}")
                return []
            return os.listdir(self.sound_path)
        except Exception as e:
            self._log_event("ERROR", "Failed to List Media Files", str(e))
            return []

    def upload_media(self, media_path: str):
        try:
            if not os.path.isfile(media_path):
                self._log_event("ERROR", "Media Upload Failed", f"Media file not found: {media_path}")
                return False
                
            if not self.sound_path:
                self._log_event("ERROR", "Media Upload Failed", "Sound path not configured")
                return False
                
            # Create sound directory if it doesn't exist
            os.makedirs(self.sound_path, exist_ok=True)
            
            destination = os.path.join(self.sound_path, os.path.basename(media_path))
            shutil.copyfile(media_path, destination)
            self._log_event("INFO", "Media Uploaded", f"Successfully uploaded: {os.path.basename(media_path)}")
            return True
        except Exception as e:
            self._log_event("ERROR", "Media Upload Failed", f"Failed to upload {media_path}: {e}")
            return False

    def add_new_channel(self):
        channel_id = len(self.channels)
        # Set the number of channels if needed
        if channel_id >= pygame.mixer.get_num_channels():
            pygame.mixer.set_num_channels(channel_id + 1)
        
        self.channels.append(pygame.mixer.Channel(channel_id))
        self.channel_sounds.append(None)
        self.channel_states.append('stopped')
        self.channel_volumes.append(1.0)
        self.channel_positions.append(0.0)
        self.channel_loops.append(False)

    def get_number_of_channels(self):
        return len(self.channels)

    def remove_channel(self, channel_index: int):
        del self.channels[channel_index]

    def register_media_on_channel(self, media_name: str, channel: int):
        try:
            if channel >= len(self.channels):
                self._log_event("ERROR", "Invalid Channel", f"Invalid channel index: {channel}")
                return False
                
            sound_path = os.path.join(self.sound_path, media_name)
            
            if not os.path.exists(sound_path):
                self._log_event("ERROR", "Sound File Not Found", f"Sound file not found: {sound_path}")
                self.channel_sounds[channel] = None
                return False
                
            self.channel_sounds[channel] = pygame.mixer.Sound(sound_path)
            self.channel_sounds[channel].set_volume(self.channel_volumes[channel])
            self._log_event("INFO", "Media Registered", f"Media registered on channel {channel}: {media_name}")
            return True
        except pygame.error as e:
            self._log_event("ERROR", "Sound Load Failed", f"Failed to load sound {media_name}: {e}")
            self.channel_sounds[channel] = None
            return False
        except Exception as e:
            self._log_event("ERROR", "Media Registration Error", f"Unexpected error registering media {media_name}: {e}")
            self.channel_sounds[channel] = None
            return False

    def put_media_in_queue(self, media_name: str, channel: int, priority: int):
        audio = Media(media_name=media_name, channel=channel)
        self.priorityQueue.put((priority, audio))

    def play_media(self, channel: int):
        try:
            if channel >= len(self.channels):
                self._log_event("ERROR", "Invalid Channel", f"Invalid channel index: {channel}")
                return False
                
            if not self.channel_sounds[channel]:
                self._log_event("WARNING", "No Sound Loaded", f"No sound loaded on channel {channel}")
                return False
                
            if self.channels[channel].get_busy():
                # Don't log this as it's normal behavior
                return False
                
            loops = -1 if self.channel_loops[channel] else 0
            self.channels[channel].play(self.channel_sounds[channel], loops=loops)
            self.channel_states[channel] = 'playing'
            self._log_event("INFO", "Media Playing", f"Started playing on channel {channel}")
            return True
        except Exception as e:
            self._log_event("ERROR", "Playback Failed", f"Failed to play media on channel {channel}: {e}")
            return False

    def play_from_queue(self):
        while not self.priorityQueue.empty():
            p, item = self.priorityQueue.get()
            if self.channels[item.channel].get_busy():
                self.priorityQueue.put((p, item))
            else:
                self.register_media_on_channel(item.mediaName, item.channel)
                self.play_media(item.channel)
            time.sleep(0.1)

    def stop_media_on_channel(self, channel: int):
        self.channels[channel].stop()
        self.channel_states[channel] = 'stopped'

    def pause_media_on_channel(self, channel: int):
        self.channels[channel].pause()
        self.channel_states[channel] = 'paused'

    def set_pause_on_channel(self, channel: int, pause: bool):
        if pause:
            self.channels[channel].pause()
            self.channel_states[channel] = 'paused'
        else:
            self.channels[channel].unpause()
            self.channel_states[channel] = 'playing'

    def get_state_of_channel(self, channel: int):
        if self.channels[channel].get_busy():
            return 'playing'
        return self.channel_states[channel]

    def get_channel_position(self, channel: int):
        # pygame doesn't provide position info, return stored position
        return self.channel_positions[channel]

    def set_volume_on_channel(self, value: int, channel):
        volume = value / 100.0  # Convert from 0-100 to 0.0-1.0
        self.channel_volumes[channel] = volume
        if self.channel_sounds[channel]:
            self.channel_sounds[channel].set_volume(volume)

    def play(self, channel: int):
        self.play_media(channel)

    def set_channel_loop_state(self, channel: int, state: bool):
        self.channel_loops[channel] = state

    def refresh_channel(self, channel: int):
        # For pygame, we just stop and reset the channel
        self.stop_media_on_channel(channel)
        self.channel_positions[channel] = 0.0

    def un_initialize(self):
        try:
            self._log_event("INFO", "Audio Service Shutdown", "Shutting down audio service...")
            print(" Shutting down audio service...")
            channels_number = self.get_number_of_channels()

            for i in range(channels_number):
                try:
                    self.stop_media_on_channel(channel=i)
                except Exception as e:
                    self._log_event("ERROR", "Channel Stop Error", f"Error stopping channel {i}: {e}")

            self.channels.clear()
            self.channel_sounds.clear()
            self.channel_states.clear()
            self.channel_volumes.clear()
            self.channel_positions.clear()
            self.channel_loops.clear()
            
            pygame.mixer.quit()
            self._log_event("INFO", "Audio Service Shutdown", "Audio service shut down successfully")
            print(" Audio service shut down successfully")
        except Exception as e:
            self._log_event("ERROR", "Shutdown Error", f"Error during audio service shutdown: {e}")

import os

from repo.repositories import AudioEventsRepository
from services.media.pygame_media_service import PygameMediaService


class PygameAudioService(PygameMediaService):
    def __init__(self):
        super(PygameAudioService, self).__init__()

    @staticmethod
    def get_events():
        return ['ENTRY', 'EXIT', 'ROBOT DISCONNECTED', 'KEYENCE DISCONNECTED', 'GOCATOR DISCONNECTED', 'MUSIC ON',
                'MUSIC OFF']

    def create_repository(self):
        self.repository = AudioEventsRepository()
        self.repository.register_callback(self.init_sound_path)

    def init_sound_path(self):
        if self.repository.get_configuration_path() != '':
            self.sound_path = self.repository.get_configuration_path() + "/music"

            if not os.path.isdir(self.sound_path):
                os.makedirs(self.sound_path)

    def play_media(self, channel: int):
        self.channels[channel].play()

import threading
import time

from repo.repositories import AudioEventsRepository
from services.media.pygame_audio_service import PygameAudioService


class EventSoundThread:
    def __init__(self, sound_service: PygameAudioService, audio_event_repo: AudioEventsRepository):
        super().__init__()
        self.soundService = sound_service
        self.audioEventRepository = audio_event_repo

        self.timeout = 0
        self.event = None
        self.running = False
        self.currentState = None
        self.currentCommand = None
        self.currentSerialNr = None

        self.execThread = None
        self.runningLock = threading.Lock()

        self.init_channels()

    def init_channels(self):
        audio_config = self.audioEventRepository.get()

        if len(audio_config) != 0:
            audio_config = audio_config[0]

        channels = -1

        for value in audio_config.values():
            if value["channel"] > channels:
                channels = value["channel"]

        channels += 1

        if channels != 0:
            for i in range(channels):
                self.soundService.add_new_channel()

    def on_sound_event(self, event_info: str):
        if not self.is_running():
            self.set_event(event_info[0])
            self.currentSerialNr = event_info[1]
            self.start()
            # self.quit()

    def state_changed(self, state: list):
        self.currentCommand = state[0]
        if self.currentCommand == "0":
            if state[1].serial_nr == self.currentSerialNr:
                self.currentState = state[1].state

    def set_timeout(self, timeout: int):
        self.timeout = timeout

    def set_event(self, event: str):
        self.event = event

    def set_running(self, value: bool):
        self.runningLock.acquire()
        self.running = value
        self.runningLock.release()

    def is_running(self):
        self.runningLock.acquire()
        running = self.running
        self.runningLock.release()
        return running

    def run(self):
        start = time.time()
        play = True
        audio_config = self.audioEventRepository.get()

        if len(audio_config) != 0:
            audio_config = audio_config[0]

        self.timeout = audio_config[self.event]["timeout"]
        while True:
            if time.time() - start >= self.timeout:
                break

            self.runningLock.acquire()
            if not self.running:
                break
            self.runningLock.release()

        if play:
            self.soundService.put_media_in_queue(media_name=audio_config[self.event]["path"],
                                                 channel=audio_config[self.event]["channel"],
                                                 priority=audio_config[self.event]["priority"])
            self.soundService.set_volume_on_channel(value=audio_config[self.event]["volume"],
                                                    channel=audio_config[self.event]["channel"])
            self.soundService.play_from_queue()
        self.set_running(False)

    def start(self):
        self.execThread = threading.Thread(target=self.run)
        self.set_running(True)
        self.execThread.start()

    def quit(self):
        if self.execThread is not None:
            self.execThread.join()
        self.execThread = None

        channels = self.soundService.get_number_of_channels()

        for i in range(channels):
            self.soundService.stop_media_on_channel(i)

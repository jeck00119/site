from services.logger.formatter import TraceabilityFormatter
from services.logger.handler import FileHandler
from services.logger.logger_model import Entry
from src.metaclasses.singleton import Singleton


class Logger(metaclass=Singleton):
    def __init__(self):
        self.handler = None

    def create_handler(self):
        pass

    def read(self):
        if self.handler:
            return self.handler.read()

        return None

    def add(self, entry: Entry):
        if self.handler:
            self.handler.write(entry)

    def remove(self, idx: int):
        if self.handler:
            self.handler.remove(idx)


class AppLogger(Logger):
    def __init__(self):
        super(AppLogger, self).__init__()

    def create_handler(self):
        self.handler = FileHandler(file_path="app.log")
        formatter = TraceabilityFormatter()
        self.handler.set_formatter(formatter)
        self.handler.init()

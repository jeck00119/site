import os

from filelock import FileLock

from services.logger.formatter import Formatter
from services.logger.logger_model import Entry


class Handler:
    def __init__(self):
        self.formatter = None

    def init(self):
        pass

    def set_formatter(self, formatter: Formatter):
        self.formatter = formatter

    def write(self, message: Entry):
        pass

    def read(self):
        pass

    def remove(self,  idx):
        pass


class ConsoleHandler(Handler):
    def __init__(self):
        super(ConsoleHandler, self).__init__()

    def init(self):
        pass

    def write(self, message: Entry):
        if self.formatter:
            output = self.formatter.format(message)
        else:
            output = message.__str__()

    def read(self):
        return None

    def remove(self, idx: int):
        pass


class FileHandler(Handler):
    def __init__(self, file_path: str):
        super(FileHandler, self).__init__()
        self.lock = FileLock(f"{file_path.split('.')[0]}.lock")
        self.path = file_path

    def init(self):
        if not os.path.exists(self.path):
            open(self.path, 'w+').close()

    def write(self, message: Entry):
        if self.formatter:
            output = self.formatter.format(message)
        else:
            output = message.__str__()

        with self.lock:
            with open(self.path, 'a') as log_file:
                log_file.write(f"{output}\n")

    def read(self):
        entries = []
        with self.lock:
            with open(self.path, 'r') as log_file:
                logs = log_file.readlines()
                logs = [log.strip() for log in logs]
                for log in logs:
                    entry = self.formatter.unzip(log)
                    entries.append(entry)

        return entries

    def remove(self, idx: int):
        with self.lock:
            with open(self.path, 'r') as log_file:
                lines = log_file.readlines()

            with open(self.path, 'w') as log_file:
                for i, line in enumerate(lines):
                    if i != idx:
                        log_file.write(line)

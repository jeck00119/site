import json

from services.logger.logger_model import AppEntry, Entry


class Formatter:
    def __init__(self):
        pass

    @staticmethod
    def format(message: Entry):
        pass

    @staticmethod
    def unzip(log_entry: str):
        pass


class TraceabilityFormatter(Formatter):
    def __init__(self):
        super(TraceabilityFormatter, self).__init__()

    @staticmethod
    def format(message: AppEntry):
        return f'{message.timestamp};{message.user};{message.type};{message.title};{message.description};{message.details}'

    @staticmethod
    def unzip(log_entry: str):
        timestamp, user, log_type, title, description, details_str = log_entry.split(';')

        details_lst = json.loads(details_str)

        return {
            'timestamp': timestamp,
            'user': user,
            'type': log_type,
            'title': title,
            'description': description,
            'details': details_lst
        }

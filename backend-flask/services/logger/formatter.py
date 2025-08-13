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
        try:
            # Try to parse the standard format
            parts = log_entry.split(';')
            if len(parts) == 6:
                timestamp, user, log_type, title, description, details_str = parts
                
                # Handle empty or invalid details
                try:
                    if details_str and details_str.strip():
                        details_lst = json.loads(details_str)
                    else:
                        details_lst = []
                except (json.JSONDecodeError, ValueError):
                    details_lst = []
                
                return {
                    'timestamp': timestamp,
                    'user': user,
                    'type': log_type,
                    'title': title,
                    'description': description,
                    'details': details_lst
                }
            else:
                # Return a default entry for malformed log lines
                return {
                    'timestamp': '',
                    'user': 'system',
                    'type': 'ERROR',
                    'title': 'Malformed log entry',
                    'description': log_entry[:100],  # First 100 chars
                    'details': []
                }
        except Exception as e:
            # Return a safe default for any parsing errors
            return {
                'timestamp': '',
                'user': 'system',
                'type': 'ERROR',
                'title': 'Log parsing error',
                'description': str(e),
                'details': []
            }

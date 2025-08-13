class UidNotUnique(Exception):
    def __init__(self):
        super().__init__()


class UidNotFound(Exception):
    def __init__(self, message=None):
        super().__init__(message or "Entity not found")


class NoConfigurationChosen(Exception):
    def __init__(self):
        super(NoConfigurationChosen, self).__init__("No configuration was set!")


class UserNotFound(Exception):
    def __init__(self):
        super(UserNotFound, self).__init__("User was not found!")

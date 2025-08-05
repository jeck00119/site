class Media:
    def __init__(self, media_name, channel):
        self.mediaName = media_name
        self.channel = channel

    def __lt__(self, other):
        return False

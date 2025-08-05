class Point:
    def __init__(self, x, y):
        self.x = x
        self.y = y

    def set(self, x, y):
        self.x = x
        self.y = y

    def get_x(self):
        return self.x

    def get_y(self):
        return self.y

    # set the print_debuged text of the class
    def __str__(self):
        return "X: " + str(self.x) + " / Y: " + str(self.y)
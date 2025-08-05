class AlgorithmException(Exception):
    pass


class InvalidImageDepthException(AlgorithmException):
    def __init__(self, expected_depth, image_depth):
        self.message = "The algorithm requires an image with a depth of " + str(expected_depth) + \
                       ", but an image with a depth of " + str(image_depth) + " was provided."


class RoiOutOfImageBoundsException(AlgorithmException):
    def __init__(self):
        self.message = "The ROI exceeds the limits of the image."

    def __repr__(self):
        return self.message

    def __str__(self):
        return self.message


class ReferenceNotFound(AlgorithmException):
    def __init__(self):
        self.message = "Reference was not found."

    def __repr__(self):
        return self.message

    def __str__(self):
        return self.message


class ReferenceNotProcessed(AlgorithmException):
    def __init__(self):
        self.message = "Reference was not processed."

    def __repr__(self):
        return self.message

    def __str__(self):
        return self.message

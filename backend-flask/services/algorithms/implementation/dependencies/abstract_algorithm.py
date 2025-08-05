import copy

import cv2
import numpy as np

from services.algorithms.implementation.dependencies.detection_calculations import Point


class AbstractAlgorithm(object):
    """
        This class represents the base class for all implemented algorithms.
        The developer is obligated to inherit the AbstractAlgorithm and implement the execute and from_dict methods.
    """

    HELP = "Verify the manual or ask the developer for more help."

    def __init__(self, graphics, reference_algorithm=None, golden_position=None, inspection_name = None):
        super(AbstractAlgorithm, self).__init__()
        self.algorithm_result = None
        self.graphics = graphics
        self.reference_algorithm = reference_algorithm
        self.golden_position = golden_position
        self.reference_point_idx = 0
        self.inspection_name = inspection_name

    def set_reference_algorithm(self, reference_algorithm):
        self.reference_algorithm = reference_algorithm

    def set_golden_position(self, golden_position):
        self.golden_position = golden_position

    def set_graphics(self, graphics):
        self.graphics = graphics

    def get_graphics(self):
        return self.graphics

    def set_reference_point_idx(self, reference_idx):
        self.reference_point_idx = reference_idx

    def to_dict(self):
        """
        This method returns the json representation of the algorithm.
        :return: a dictionary
        """
        data = self.__dict__
        data_deepc = copy.deepcopy(data)

        try:
            del data_deepc["reference_algorithm"]
        except KeyError:
            pass

        try:
            del data_deepc["golden_position"]
        except KeyError:
            pass

        try:
            del data_deepc["algorithm_result"]
        except KeyError:
            pass

        del_keys = []
        for key in data_deepc:
            if '_NOT' in key:
                del_keys.append(key)
        for key in del_keys:
            del data_deepc[key]
        return data_deepc

    @classmethod
    def from_dict(cls, algorithm: dict, reference_algorithm=None, golden_position=None):
        """
        This method creates an instance of the desired Algorithm
        :param algorithm: a dictionary
        :param reference_algorithm reference algorithm
        :param golden_position list of 2 values
        :return: an instance of AbstractAlgorithm
        """
        return cls(algorithm)

    def add_inspection_name(self, str):
        self.inspection_name = str

    def execute(self, frame: np.ndarray):

        """
        This method does the algorithm execution
        :param frame: a BGR opencv frame of type np.ndarray
        :return: It returns an instance of AlgorithmResult
        """
        pass

    def compute_displacement(self, ref: Point):
        print(f"REF: {ref}")
        x_displacement = None
        y_displacement = None

        if self.golden_position is not None and len(self.golden_position) != 0 and ref.x is not None:
            x_displacement = ref.x - self.golden_position[0]
            y_displacement = ref.y - self.golden_position[1]

        return Point(x_displacement, y_displacement)

    @staticmethod
    def mask_region(roi, mask, color):
        arr = np.array(mask, dtype=np.int32)
        masked = cv2.fillPoly(roi, [arr], color=(color[0], color[1], color[2]))
        return masked

import copy
import random

import cv2
import numpy as np

from services.algorithms.implementation.dependencies.abstract_algorithm import AbstractAlgorithm
from services.algorithms.implementation.dependencies.algorithm_result import AlgorithmResult
from src.utils import crop_roi


class GraphSegmentationAlgorithm(AbstractAlgorithm):
    def __init__(self, k, min_size: int, segmentation_type: str, blur_kernel_size: int, sigma: float,
                 graphics, reference_algorithm=None, golden_position=None):
        super(GraphSegmentationAlgorithm, self).__init__(graphics, reference_algorithm=reference_algorithm,
                                                         golden_position=golden_position)
        self.k = k
        self.min_size = min_size
        self.segmentation_type = segmentation_type
        self.blur_kernel_size = blur_kernel_size
        self.sigma = sigma

    def execute(self, frame: np.ndarray):
        self.algorithm_result = AlgorithmResult()

        graphics_copy = copy.deepcopy(self.graphics)

        if self.reference_algorithm is not None:
            algorithm_result = self.reference_algorithm.execute(frame)
            if algorithm_result.data is not None:
                reference = algorithm_result.referencePoint
                if reference.x is not None:
                    for roi in graphics_copy:
                        roi["bound"][0] += reference.x
                        roi["bound"][1] += reference.y

        roi, coordinates = crop_roi(frame, roi_offset=graphics_copy[0]["offset"],
                                    roi_bound=graphics_copy[0]["bound"], roi_rect=graphics_copy[0]["rect"],
                                    rotation=graphics_copy[0]["rotation"])

        height, width = roi.shape[:2]
        roi = cv2.GaussianBlur(roi, (self.blur_kernel_size, self.blur_kernel_size), self.sigma)
        gray = cv2.cvtColor(roi, cv2.COLOR_BGR2GRAY)

        if self.segmentation_type == "GRAYSCALE":
            down_cost = abs(gray[1:, :] - gray[:height - 1, :])
            right_cost = abs(gray[:, 1:] - gray[:, :width - 1])
            down_right_cost = abs(gray[1:, 1:] - gray[:height - 1, :width - 1])
            up_right_cost = abs(gray[1:, :width - 1] - gray[:height - 1, 1:])
        else:
            down_cost = np.sqrt(np.sum((roi[1:, :, :] - roi[:height - 1, :, :]) *
                                       (roi[1:, :, :] - roi[:height - 1, :, :]), axis=-1))
            right_cost = np.sqrt(np.sum((roi[:, 1:, :] - roi[:, :width - 1, :]) *
                                        (roi[:, 1:, :] - roi[:, :width - 1, :]), axis=-1))
            down_right_cost = np.sqrt(np.sum((roi[1:, 1:, :] - roi[:height - 1, :width - 1, :]) *
                                             (roi[1:, 1:, :] - roi[:height - 1, :width - 1, :]), axis=-1))
            up_right_cost = np.sqrt(np.sum((roi[1:, :width - 1, :] - roi[:height - 1, 1:, :]) *
                                           (roi[1:, :width - 1, :] - roi[:height - 1, 1:, :]), axis=-1))

        costs = np.hstack([right_cost.ravel(), down_cost.ravel(), down_right_cost.ravel(), up_right_cost.ravel()])

        segments = np.arange(stop=width * height, dtype=np.uint32).reshape(height, width)

        down_edges = np.c_[segments[1:, :].ravel(), segments[:height - 1, :].ravel()]
        right_edges = np.c_[segments[:, 1:].ravel(), segments[:, :width - 1].ravel()]
        down_right_edges = np.c_[segments[1:, 1:].ravel(), segments[:height - 1, :width - 1].ravel()]
        up_right_edges = np.c_[segments[:height - 1, 1:].ravel(), segments[1:, :width - 1].ravel()]
        edges = np.vstack([right_edges, down_edges, down_right_edges, up_right_edges])

        edge_queue = np.argsort(costs)
        edges = np.ascontiguousarray(edges[edge_queue])
        costs = np.ascontiguousarray(costs[edge_queue])

        segment_size = np.ones(width * height, dtype=np.int32)
        cint = np.zeros(width * height)

        segments = segments.flatten()

        num_costs = costs.size

        for i in range(num_costs):
            seg0 = self.find_root(segments, edges[i][0])
            seg1 = self.find_root(segments, edges[i][1])

            if seg0 == seg1:
                continue
            else:
                inner_cost0 = cint[seg0] + self.k / segment_size[seg0]
                inner_cost1 = cint[seg1] + self.k / segment_size[seg1]

                if costs[i] < min(inner_cost0, inner_cost1):
                    self.join_trees(segments, seg0, seg1)
                    seg_new = self.find_root(segments, seg0)
                    segment_size[seg_new] = segment_size[seg0] + segment_size[seg1]
                    cint[seg_new] = costs[i]

        for i in range(num_costs):
            seg0 = self.find_root(segments, edges[i][0])
            seg1 = self.find_root(segments, edges[i][1])

            if seg0 == seg1:
                continue
            else:
                if segment_size[seg0] < self.min_size or segment_size[seg1] < self.min_size:
                    self.join_trees(segments, seg0, seg1)
                    seg_new = self.find_root(segments, seg0)
                    segment_size[seg_new] = segment_size[seg0] + segment_size[seg1]

        res = np.zeros(shape=(segments.shape[0], 3), dtype=np.uint8)
        unique_segments = np.unique(segments)

        for i in range(unique_segments.shape[0]):
            color = [random.randint(0, 255), random.randint(0, 255), random.randint(0, 255)]
            r = np.where(segments == unique_segments[i])
            res[r] = color

        res = np.reshape(a=res, newshape=(height, width, 3))

        self.algorithm_result.debugImages = [roi, res]
        self.algorithm_result.imageRoi = res

        return self.algorithm_result

    @staticmethod
    def find_root(forest: np.ndarray, node: int):
        root = node
        while forest[root] < root:
            root = forest[root]
        return root

    @staticmethod
    def set_root(forest: np.ndarray, node: int, root: int):
        res = np.where(forest == node)
        forest[res] = root

        forest[node] = root

    def join_trees(self, forest: np.ndarray, node1: int, node2: int):
        if node1 != node2:
            root = None

            if node1 > node2:
                root = node2
            else:
                root = node1

            self.set_root(forest, node1, root)
            self.set_root(forest, node2, root)

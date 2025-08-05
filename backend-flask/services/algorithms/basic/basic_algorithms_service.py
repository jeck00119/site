from inspect import signature
from typing import Union

import numpy as np

from services.algorithms.basic.basic_algorithms_factory import BasicAlgorithmFactory
from services.algorithms.basic.dependencies.compound_algorithm import CompoundAlgorithm
from services.algorithms.basic.models.basic_algorithms_models import EnumBasicAlgorithmType, \
    BilateralFilterAlgorithmModel, BinarizationAlgorithmModel, DmcAlgorithmModel, \
    DoubleThresholdBinarizationAlgorithmModel, OpeningAlgorithmModel, BoxBlurAlgorithmModel, \
    EdgeDetectionAlgorithmModel, GrayscaleAlgorithmModel, ExtractRegionAlgorithmModel
from services.algorithms.basic.models.data_representation import NumpyType, ListType, DictType, IntegerType, \
    CompoundBlock, SimpleBlock
from services.services_exceptions import NoLiveAlgSet
from src.metaclasses.singleton import Singleton
from src.utils import frame_to_base64


class BasicAlgorithmsService(metaclass=Singleton):
    def __init__(self):
        self.live_algorithm: Union[None, CompoundAlgorithm] = None
        self.blocks = []
        self.algorithm_types = []
        self.compound_block = None

    def get_live_algorithm(self):
        return self.live_algorithm

    def get_compound_block(self):
        if self.compound_block:
            return self.compound_block.get_blocks()

        return None

    def set_blocks(self, data_blocks: list):
        self.blocks = data_blocks

    def set_algorithm_types(self, algorithm_types):
        self.algorithm_types = algorithm_types

    def set_live_algorithm(self):
        self.compound_block = CompoundBlock()
        compound_algorithm = CompoundAlgorithm(compound_block=self.compound_block)

        for algorithm_type in self.algorithm_types:
            algorithm = BasicAlgorithmFactory.create_algorithm(algorithm_type, self.get_model_from_type(algorithm_type))

            ins, outs = self.create_inputs_outputs_objects(algorithm)

            sb = SimpleBlock(ins, outs, algorithm_type)

            self.compound_block.add(sb)
            compound_algorithm.add(algorithm=algorithm)

        self.connect_blocks(compound_block=self.compound_block, data_blocks=self.blocks)

        self.live_algorithm = compound_algorithm

    @staticmethod
    def connect_blocks(compound_block, data_blocks):
        for i in range(len(compound_block.blocks)):
            # i -> index for the block
            for j in range(len(compound_block.blocks[i].ins)):
                # j -> index for the input of the block
                # if there's no connection for this input, saved value is -1
                if data_blocks[i]['blockIndex'][j] != -1:
                    # index of the block which is output is connected to this input
                    block_index = data_blocks[i]['blockIndex'][j]
                    # output index of the block
                    output_index = data_blocks[i]['outputIndex'][j]

                    # make the connection between the input and the output for this block
                    compound_block.blocks[i].ins[j] = compound_block.blocks[block_index].outs[output_index]

    def create_inputs_outputs_objects(self, simple_algorithm):
        sig = signature(simple_algorithm.operation)

        parameters = sig.parameters

        ins = []
        outs = []

        for name, parameter in parameters.items():
            if name.startswith("out"):
                outs.append(self.create_object_from_type(parameter.annotation))
            else:
                ins.append(self.create_object_from_type(parameter.annotation))

        return ins, outs

    @staticmethod
    def create_object_from_type(t):
        if t is NumpyType:
            return NumpyType()
        elif t is ListType:
            return ListType()
        elif t is DictType:
            return DictType()
        elif t is IntegerType:
            return IntegerType()
        else:
            return None

    def release_algorithm(self):
        self.live_algorithm = None

    def execute_algorithm(self, frame=None):
        self.live_algorithm.execute(frame)

    def edit_live_algorithm_field(self, idx, key, val):
        if self.live_algorithm is not None:
            self.live_algorithm.set_attribute(idx, key, val)
        else:
            raise NoLiveAlgSet

    def edit_live_algorithm(self, idx, data: dict):
        if self.live_algorithm is not None:
            for key, val in data.items():
                self.live_algorithm.set_attribute(idx, key, val)
        else:
            raise NoLiveAlgSet

    def set_input_frame(self, frame):
        if self.compound_block:
            self.compound_block.blocks[0].ins[0].set_value(frame)

    @staticmethod
    def get_model_from_type(algorithm_type):
        if algorithm_type == EnumBasicAlgorithmType.bilateral_filter:
            return BilateralFilterAlgorithmModel()
        if algorithm_type == EnumBasicAlgorithmType.binarization:
            return BinarizationAlgorithmModel()
        if algorithm_type == EnumBasicAlgorithmType.dmc:
            return DmcAlgorithmModel()
        if algorithm_type == EnumBasicAlgorithmType.double_threshold_binarization:
            return DoubleThresholdBinarizationAlgorithmModel()
        if algorithm_type == EnumBasicAlgorithmType.opening:
            return OpeningAlgorithmModel()
        if algorithm_type == EnumBasicAlgorithmType.box_blur:
            return BoxBlurAlgorithmModel()
        if algorithm_type == EnumBasicAlgorithmType.edge_detection:
            return EdgeDetectionAlgorithmModel()
        if algorithm_type == EnumBasicAlgorithmType.grayscale:
            return GrayscaleAlgorithmModel()
        if algorithm_type == EnumBasicAlgorithmType.extract_region:
            return ExtractRegionAlgorithmModel()

    @staticmethod
    def get_ui_from_type(algorithm_type):
        if algorithm_type == EnumBasicAlgorithmType.bilateral_filter:
            return [
                {
                    'name': 'diameter',
                    'type': 'integer',
                    'default': 1
                },
                {
                    'name': 'sigmaColor',
                    'type': 'integer',
                    'default': 1
                },
                {
                    'name': 'sigmaSpace',
                    'type': 'integer',
                    'default': 1
                },
                {
                    'name': 'borderType',
                    'type': 'dropdown',
                    'default': 'DEFAULT',
                    'values': ['DEFAULT', 'REPLICATE', 'REFLECT', 'WRAP', 'TRANSPARENT']
                }
            ]
        elif algorithm_type == EnumBasicAlgorithmType.binarization:
            return [
                {
                    'name': 'threshold',
                    'type': 'integer',
                    'default': 0
                }
            ]
        elif algorithm_type == EnumBasicAlgorithmType.dmc:
            return [
                {
                    'name': 'charNumber',
                    'type': 'integer',
                    'default': 0
                },
                {
                    'name': 'threshold',
                    'type': 'integer',
                    'default': 0
                },
                {
                    'name': 'gapSize',
                    'type': 'integer',
                    'default': 0
                },
                {
                    'name': 'shrink',
                    'type': 'integer',
                    'default': 1
                },
                {
                    'name': 'deviation',
                    'type': 'integer',
                    'default': 0
                },
                {
                    'name': 'shape',
                    'type': 'integer',
                    'default': 0
                },
                {
                    'name': 'corrections',
                    'type': 'integer',
                    'default': 0
                },
                {
                    'name': 'maxCount',
                    'type': 'integer',
                    'default': 0
                },
                {
                    'name': 'timeout',
                    'type': 'integer',
                    'default': 0
                },
                {
                    'name': 'minEdge',
                    'type': 'integer',
                    'default': 0
                },
                {
                    'name': 'maxEdge',
                    'type': 'integer',
                    'default': 0
                }
            ]
        elif algorithm_type == EnumBasicAlgorithmType.double_threshold_binarization:
            return [
                {
                    'name': 'firstThreshold',
                    'type': 'integer',
                    'default': 0
                },
                {
                    'name': 'secondThreshold',
                    'type': 'integer',
                    'default': 0
                }
            ]
        elif algorithm_type == EnumBasicAlgorithmType.opening:
            return [
                {
                    'name': 'kernelSize',
                    'type': 'integer',
                    'default': 1
                }
            ]
        elif algorithm_type == EnumBasicAlgorithmType.box_blur:
            return [
                {
                    'name': 'kernelSize',
                    'type': 'integer',
                    'default': 1
                }
            ]
        elif algorithm_type == EnumBasicAlgorithmType.edge_detection:
            return [
                {
                    'name': 'cannyFirstThreshold',
                    'type': 'integer',
                    'default': 30
                },
                {
                    'name': 'cannySecondThreshold',
                    'type': 'integer',
                    'default': 200
                }
            ]
        elif algorithm_type == EnumBasicAlgorithmType.grayscale:
            return []
        elif algorithm_type == EnumBasicAlgorithmType.extract_region:
            return [
                {
                    'name': 'graphics',
                    'type': 'list',
                    'default': [
                        {
                            "rotation": 0,
                            "bound": [
                                10,
                                10,
                                100,
                                100
                            ],
                            "offset": [
                                0,
                                0
                            ],
                            "rect": [
                                10,
                                10,
                                100,
                                100
                            ]
                        }
                    ]
                }
            ]
        else:
            return []

    @staticmethod
    def list_algorithms_types():
        return EnumBasicAlgorithmType.list()

    def list_algorithm_types_and_params(self):
        algorithm_types = self.list_algorithms_types()

        types = []
        for algorithm_type in algorithm_types:
            data = {
                'name': algorithm_type
            }

            algorithm = BasicAlgorithmFactory.create_algorithm(algorithm_type, self.get_model_from_type(algorithm_type))

            sig = signature(algorithm.operation)

            parameters = sig.parameters

            ins = []
            outs = []

            for name, parameter in parameters.items():
                parameter_type = str(parameter.annotation)
                parameter_type = parameter_type[parameter_type.rfind('.') + 1:parameter_type.rfind('\'')]

                if name.startswith('out'):
                    outs.append({
                        'name': name,
                        'type': parameter_type
                    })
                else:
                    ins.append({
                        'name': name,
                        'type': parameter_type
                    })

            data['inputs'] = ins
            data['outputs'] = outs

            types.append(data)

        return types

    def get_compound_result(self, decode=False):
        results = []

        compound_block = self.get_compound_block()

        if compound_block:
            for block_idx, block in enumerate(compound_block):
                data = {
                    'inputs': [],
                    'outputs': []
                }

                for alg_input in block.ins:
                    if isinstance(alg_input, NumpyType):
                        val = alg_input.value()
                    else:
                        val = np.zeros(shape=(128, 128), dtype=np.uint8)

                    if decode:
                        val = frame_to_base64(val).decode('utf-8')
                    else:
                        val = frame_to_base64(val)

                    data['inputs'].append(val)

                for i, alg_output in enumerate(block.outs):
                    if isinstance(alg_output, NumpyType):
                        val = alg_output.value()
                    else:
                        val = np.zeros(shape=(128, 128), dtype=np.uint8)

                    if decode:
                        val = frame_to_base64(val).decode('utf-8')
                    else:
                        val = frame_to_base64(val)

                    data['outputs'].append(val)

                results.append(data)

        return results

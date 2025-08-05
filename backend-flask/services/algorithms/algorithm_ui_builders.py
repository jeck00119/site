from enum import Enum

from services.algorithms.algorithms_models import EnumAlgorithmType


class AlgUiFactory:
    def __init__(self):
        pass

    @staticmethod
    def create_algorithm_ui(algorithm_type):
        if EnumAlgorithmType.basic_binarization == algorithm_type:
            return [
                AlgUi(name='binary_threshold',
                      default_value=120,
                      label="Binarization Threshold",
                      tooltip='',
                      type='integer',
                      active='True').__dict__,
                AlgUi(name='white_ratio',
                      default_value=0.5,
                      label="White Ratio",
                      tooltip='',
                      type='float',
                      active='True').__dict__,
                AlgUi(name='binary_inverse',
                      default_value=120,
                      label="Binary Inverse",
                      tooltip='',
                      type='bool',
                      active='True').__dict__,
            ]
        elif EnumAlgorithmType.blob ==algorithm_type:
            return [
                AlgUi(name='binary_threshold',
                      label="Binarization Threshold",
                      type=AlgUiTypes.int,
                      default_value=120,
                      active='True',
                      tooltip='').__dict__,

                AlgUi(name='opening',
                      label="Opening",
                      type=AlgUiTypes.int,
                      default_value=1,
                      active='True',
                      tooltip='').__dict__,

                AlgUi(name='closing',
                      label="Closing",
                      default_value=1,
                      type=AlgUiTypes.int,
                      active='True',
                      tooltip='').__dict__,

                AlgUi(name='ph1',
                      label="ph1",
                      type=AlgUiTypes.int,
                      default_value=1,
                      active='True',
                      tooltip='', ).__dict__,

                AlgUi(name='ph2',
                      label="ph2",
                      type=AlgUiTypes.int,
                      default_value=1,
                      active='True',
                      tooltip='').__dict__,

                AlgUi(name='area_enable',
                      label="area_enable",
                      type=AlgUiTypes.bool,
                      default_value=True,
                      active='True',
                      tooltip='').__dict__,

                AlgUi(name='circle_enable',
                      label="circle_enable",
                      type=AlgUiTypes.bool,
                      default_value=True,
                      active='True',
                      tooltip='').__dict__,

                AlgUi(name='conv_enable',
                      label="conv_enable",
                      type=AlgUiTypes.bool,
                      default_value=True,
                      active='True',
                      tooltip='').__dict__,

                AlgUi(name='inert_enable',
                      label="inert_enable",
                      type=AlgUiTypes.bool,
                      default_value=True,
                      active='True',
                      tooltip='').__dict__,

                AlgUi(name='area_value',
                      label="area_value",
                      type=AlgUiTypes.int,
                      default_value=1,
                      active='True',
                      tooltip='').__dict__,

                AlgUi(name='circle_value',
                      label="circle_value",
                      type=AlgUiTypes.int,
                      default_value=1,
                      active='True',
                      tooltip='').__dict__,

                AlgUi(name='conv_value',
                      label="conv_value",
                      type=AlgUiTypes.float,
                      default_value=1,
                      active='True',
                      tooltip='').__dict__,

                AlgUi(name='inert_value',
                      label="inert_value",
                      type=AlgUiTypes.float,
                      default_value=1,
                      active='True',
                      tooltip='').__dict__,

                AlgUi(name='results_number',
                      label="results_number",
                      type=AlgUiTypes.int,
                      default_value=1,
                      active='True',
                      tooltip='').__dict__,

                AlgUi(name='results_names',
                      label="result_names",
                      type=AlgUiTypes.list,
                      default_value=1,
                      active='True',
                      tooltip='').__dict__,
            ]

class AlgUiTypes(Enum):
    int = 'integer'
    float = 'float'
    list = 'list'
    bool = 'bool'


class AlgUi:
    def __init__(self, name, label, default_value, tooltip, type, active):
        self.label = label
        self.name = name
        self.default = default_value
        self.tooltip = tooltip
        self.type = type
        self.active = active


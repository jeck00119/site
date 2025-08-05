from services.algorithms.basic.dependencies.abstract_basic_algorithm import AbstractBasicAlgorithm
from services.algorithms.basic.models.data_representation import CompoundBlock, SimpleBlock


class CompoundAlgorithm(AbstractBasicAlgorithm):
    def __init__(self, compound_block: CompoundBlock):
        super(CompoundAlgorithm, self).__init__()
        self.algorithms: [AbstractBasicAlgorithm] = []
        self.compoundBlock = compound_block

    def add(self, algorithm: AbstractBasicAlgorithm):
        self.algorithms.append(algorithm)

    def remove(self, algorithm: AbstractBasicAlgorithm):
        self.algorithms.remove(algorithm)

    def remove_by_index(self, index: int):
        del self.algorithms[index]

    def swap(self, old_index, new_index):
        self.algorithms.insert(new_index, self.algorithms.pop(old_index))

    def set_attribute(self, idx, name, value):
        self.algorithms[idx].__setattr__(name, value)

    def execute(self, block: SimpleBlock = None):
        out = None
        for i, algorithm in enumerate(self.algorithms):
            out = algorithm.execute(block=self.compoundBlock.blocks[i])

        return out

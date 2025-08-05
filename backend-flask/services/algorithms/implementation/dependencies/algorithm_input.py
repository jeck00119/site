from abc import ABC, abstractmethod


class Type(ABC):
    def __init__(self):
        pass

    @abstractmethod
    def value(self):
        pass

    @abstractmethod
    def set_value(self, value):
        pass


class ListType(Type):
    def __init__(self):
        super(ListType, self).__init__()
        self.lst = []

    def value(self):
        return self.lst

    def set_value(self, value):
        self.lst = value


class NumpyType(Type):
    def __init__(self):
        super(NumpyType, self).__init__()
        self.array = None

    def value(self):
        return self.array

    def set_value(self, value):
        self.array = value


class IntegerType(Type):
    def __init__(self):
        super(IntegerType, self).__init__()
        self.i = None

    def value(self):
        return self.i

    def set_value(self, value):
        self.i = value


class DictType(Type):
    def __init__(self):
        super(DictType, self).__init__()
        self.dct = None

    def value(self):
        return self.dct

    def set_value(self, value):
        self.dct = value


class InOutBlock(ABC):
    def __init__(self):
        pass


class SimpleBlock(InOutBlock):
    def __init__(self, ins: [Type], outs: [Type], name=""):
        super(SimpleBlock, self).__init__()
        self.ins = ins
        self.outs = outs
        self.name = name


class CompoundBlock(InOutBlock):
    def __init__(self):
        super(CompoundBlock, self).__init__()
        self.blocks: [InOutBlock] = []

    def add(self, block: InOutBlock):
        self.blocks.append(block)

    def remove(self, block: InOutBlock):
        self.blocks.remove(block)

    def remove_by_index(self, index: int):
        del self.blocks[index]

    def swap(self, old_index, new_index):
        self.blocks.insert(new_index, self.blocks.pop(old_index))

from services.algorithms.implementation.dependencies.algorithm_input import SimpleBlock


class AbstractBasicAlgorithm():
    """
        This class represents the base class for all implemented algorithms.
        The developer is obligated to inherit the AbstractAlgorithm and implement execute and from_dict methods.
    """

    def __init__(self):
        super(AbstractBasicAlgorithm, self).__init__()

    def to_dict(self):
        """
        This method returns the json representation of the algorithm.
        :return: a dictionary
        """
        data = self.__dict__
        return data

    @classmethod
    def from_dict(cls, data: dict):
        """
        This method creates an instance of the desired AbstractBasicAlgorithm
        :param data: a dictionary
        :return: an instance of AbstractAlgorithm
        """
        return cls()

    def execute(self, block: SimpleBlock = None):
        """
        This method does the algorithm execution
        :param block: passable object between algorithms
        :return: It returns a passable object between algorithms
        """
        return block

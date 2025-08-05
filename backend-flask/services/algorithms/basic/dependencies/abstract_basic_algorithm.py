from services.algorithms.basic.models.data_representation import SimpleBlock


class AbstractBasicAlgorithm(object):
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

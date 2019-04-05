import abc


class Player(metaclass=abc.ABCMeta):

    @abc.abstractmethod
    def step(self, environment):
        pass

    @abc.abstractmethod
    def feedback(self, succeeded):
        pass

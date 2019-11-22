import abc

from hivegame.engine.hive import Hive


class Player(metaclass=abc.ABCMeta):

    @abc.abstractmethod
    def step(self, hive: 'Hive'):
        """
        Calculates or asks for the next step of the player. It does not perform the step on the engine.
        :param environment: Environment object used for asking about the state of the game. Preferably this is a
                            constant variable
        :return: A tuple of (piece, end_cell) where piece is a Piece object with which the step should be performed and
                 end_cell is the target location, where the bug should be placed or moved
        """
        pass

    @abc.abstractmethod
    def feedback(self, succeeded) -> None:
        """
        A callback of the player which should be called after performing the step on the engine.
        :param succeeded: True if the preceding step was successful, False otherwise
        """
        pass

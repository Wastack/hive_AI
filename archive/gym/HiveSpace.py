import random

from gym.spaces import Discrete

from engine.environment.aienvironment import AIEnvironment
from engine.hive import Hive
from engine import hive_representation as represent


class HiveActionSpace(Discrete):
    def _val_indices(self):
        # TODO currently only white player supported (which is indicated by 1)
        val_moves = represent.get_all_action_vector(self.env.hive)
        return [i for i, v in enumerate(val_moves) if v > 0]

    def __init__(self, hive: Hive):
        self.env = AIEnvironment()
        self.env.hive = hive
        super().__init__(self.env.getActionSize())

    def sample(self):
        val_indices = self._val_indices()
        if not val_indices:
            raise RuntimeError("Player is not able to move")
        return random.choice(val_indices)

    def contains(self, x):
        if not super().contains(x):
            return False
        if x not in self._val_indices():
            return False
        return True
import sys
import time

from PyQt5 import QtWidgets

from hivegame.AI.random_player import RandomPlayer
from hivegame.arena import Arena
from unittest import TestCase

import logging

FORMAT = "[%(filename)s:%(lineno)s - %(funcName)20s() ] %(message)s"
logging.basicConfig(level=logging.DEBUG, format=FORMAT)
logger = logging.getLogger()

class TestRandomAi(TestCase):
    """Verify the HexBoard logic"""

    def setUp(self):
        self.sh = logging.StreamHandler(sys.stdout)
        logger.addHandler(self.sh)
        self.game = Arena(RandomPlayer(), RandomPlayer())

    def test_run_against_itself(self):
        timeout = time.time() + 10 # 10 sec from now
        while time.time() < timeout:
            self.game.playGame()

    def test_representation_step(self):
        self.game = Arena(RandomPlayer(use_repr=True), RandomPlayer(use_repr=True))
        print(self.game.env.hive)
        timeout = time.time() + 10  # 10 sec
        while time.time() < timeout:
            self.game.playGame()


if __name__ == '__main__':
    FORMAT = "[%(filename)s:%(lineno)s - %(funcName)20s() ] %(message)s"
    logging.basicConfig(level=logging.DEBUG, format=FORMAT)
    import unittest
    unittest.main()

import time

from hivegame.AI.random_player import RandomPlayer

from hivegame.arena import Arena

from unittest import TestCase

class TestRandomAi(TestCase):
    """Verify the HexBoard logic"""

    def setUp(self):
        self.game = Arena(RandomPlayer(), RandomPlayer())

    def test_run_against_itself(self):
        timeout = time.time() + 10 # 10 sec from now
        while time.time() < timeout:
            self.game.playGame()
        self.game.env.logger.close()

    def test_representation_step(self):
        self.game = Arena(RandomPlayer(use_repr=True), RandomPlayer(use_repr=True))
        timeout = time.time() + 10  # 10 sec
        while time.time() < timeout:
            self.game.playGame()
        self.game.env.logger.close()


if __name__ == '__main__':
    import unittest
    unittest.main()

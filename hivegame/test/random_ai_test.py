from unittest import TestCase
import time

from hivegame.AI.random_ai import RandomAI
from hivegame.environment import Environment
from hivegame.hive import Hive
from hivegame.view import HiveView

from arena import Arena

from unittest import TestCase

class TestRandomAi(TestCase):
    """Verify the HexBoard logic"""

    def setUp(self):
        self.game = Arena(RandomAI(), RandomAI())

    def test_run_against_itself(self):
        timeout = time.time() + 10 # 10 sec from now
        while time.time() < timeout:
            self.game.run()
        self.game.env.logger.close()


if __name__ == '__main__':
    import unittest
    unittest.main()

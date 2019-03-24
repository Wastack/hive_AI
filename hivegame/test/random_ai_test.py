from unittest import TestCase
import time

from hivegame.AI.random_ai import RandomAI
from hivegame.environment import Environment
from hivegame.hive import Hive
from hivegame.view import HiveView

from unittest import TestCase

class TestRandomAi(TestCase):
    """Verify the HexBoard logic"""

    def setUp(self):
        self.env = Environment()
        self.view = HiveView(self.env.hive)

    def test_run_againt_itself(self):
        print("DEBUG: run_againt_itself start")
        ai = RandomAI()
        timeout = time.time() + 10 # 10 sec from now
        while time.time() < timeout:
            self.env.reset_game()
            while self.env.check_victory() == Hive.UNFINISHED:
                response = ai.step(self.env)
                if not response:
                    self.env.exec_cmd("pass")
                    print("DEBUG: AI passed")
                    continue
                (piece, coord) = response
                if piece.kind == 'G':
                    print(self.view)
                    print("DEBUG: choosen action is: ({}, {})".format(piece,coord) )
                    print("DEBUG: from {}".format(piece.position))
                self.env.action_piece_to(piece, coord)
        print("DEBUG: a game finished")
        self.env.logger.close()


if __name__ == '__main__':
    import unittest
    unittest.main()

import logging, sys
from unittest import TestCase

from hivegame.AI.utils import Node, ucb_score, Monte_Carlo_Tree_Search


FORMAT = "[%(filename)s:%(lineno)s - %(funcName)20s() ] %(message)s"
logging.basicConfig(level=logging.DEBUG, format=FORMAT)
logger = logging.getLogger()

class TestMonteCarlo(TestCase):

    def setUp(self):
        self.sh = logging.StreamHandler(sys.stdout)
        logger.addHandler(self.sh)

    def test_create_node(self):
        #testing node creation
        prior = 0.7
        to_play = 1
        node = Node(prior, to_play)

        self.assertEqual(node.prior, prior)
        self.assertEqual(node.to_play, to_play)

    def test_run_monte_carlo(self):
        pass


if __name__ == '__main__':
    FORMAT = "[%(filename)s:%(lineno)s - %(funcName)20s() ] %(message)s"
    logging.basicConfig(level=logging.DEBUG, format=FORMAT)
    import unittest
    unittest.main()

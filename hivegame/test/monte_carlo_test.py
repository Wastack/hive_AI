import logging, sys
from unittest import TestCase

from AI.utils import Monte_Carlo


FORMAT = "[%(filename)s:%(lineno)s - %(funcName)20s() ] %(message)s"
logging.basicConfig(level=logging.DEBUG, format=FORMAT)
logger = logging.getLogger()

class TestMonteCarlo(TestCase):

    def setUp(self):
        self.sh = logging.StreamHandler(sys.stdout)
        logger.addHandler(self.sh)

    def createNode(self):
        #testing node creation
        return


if __name__ == '__main__':
    FORMAT = "[%(filename)s:%(lineno)s - %(funcName)20s() ] %(message)s"
    logging.basicConfig(level=logging.DEBUG, format=FORMAT)
    import unittest
    unittest.main()

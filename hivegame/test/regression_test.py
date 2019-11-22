from unittest import TestCase
import logging, sys

from hivegame.utils import importexport
from engine import hive_representation as represent

FORMAT = "[%(filename)s:%(lineno)s - %(funcName)20s() ] %(message)s"
logging.basicConfig(level=logging.DEBUG, format=FORMAT)
logger = logging.getLogger()


class ResressionTest(TestCase):
    """ Verify special cases """

    def setUp(self) -> None:
        self.sh = logging.StreamHandler(sys.stdout)
        logger.addHandler(self.sh)

    def tearDown(self) -> None:
        logger.removeHandler(self.sh)

    def test_10000(self):
        hive = importexport.import_hive(importexport.saved_game_path("test_10000.json"))
        actions = represent.get_all_action_vector(hive)
        self.assertEqual(0, actions[775])


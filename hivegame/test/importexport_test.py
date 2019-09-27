import logging, sys
import os
from unittest import TestCase
import json

from hive_utils import Player
from hivegame.hive import Hive
from hivegame.utils import hexutil, importexport

FORMAT = "[%(filename)s:%(lineno)s - %(funcName)20s() ] %(message)s"
logging.basicConfig(level=logging.DEBUG, format=FORMAT)
logger = logging.getLogger()

class TestImportExport(TestCase):
    """
    Verify logic related to importing and exporting Hive state.
    """

    def setUp(self) -> None:
        self.sh = logging.StreamHandler(sys.stdout)
        logger.addHandler(self.sh)
        self.hive = Hive()

        self.hive.level.move_or_append_to(self.hive.get_piece_by_name("wS1"), hexutil.Hex(0, 0))
        self.hive.level.move_or_append_to(self.hive.get_piece_by_name("bS1"), hexutil.Hex(2, 0))
        self.hive.level.move_or_append_to(self.hive.get_piece_by_name("wQ1"), hexutil.Hex(-1, -1))
        self.hive.level.move_or_append_to(self.hive.get_piece_by_name("bQ1"), hexutil.Hex(3, -1))
        self.hive.level.move_or_append_to(self.hive.get_piece_by_name("wS2"), hexutil.Hex(-1, 1))
        self.hive.level.move_or_append_to(self.hive.get_piece_by_name("bG1"), hexutil.Hex(4, 0))
        self.hive.level.move_or_append_to(self.hive.get_piece_by_name("wB1"), hexutil.Hex(-3, 1))
        self.hive.level.move_or_append_to(self.hive.get_piece_by_name("bA1"), hexutil.Hex(2, -2))
        self.hive.level.move_or_append_to(self.hive.get_piece_by_name("wG1"), hexutil.Hex(-4, 0))
        self.hive.level.move_or_append_to(self.hive.get_piece_by_name("bB1"), hexutil.Hex(3, 1))
        self.hive.level.current_player = Player.BLACK

    def tearDown(self) -> None:
        logger.removeHandler(self.sh)

    def test_export_hive(self):
        importexport.export_hive(self.hive, importexport.saved_game_path("test_export.json"))
        exported_data = json.load(open(importexport.saved_game_path('test_export.json'), 'r'))
        test_data = json.load(open(os.path.join(os.path.dirname(__file__), "import_export_data.json"), 'r'))
        self.assertEqual(exported_data, test_data)

    def test_import_hive(self):
        file_path = os.path.join(os.path.dirname(__file__), "import_export_data.json")
        imported_hive = importexport.import_hive(file_path)

        # Current player is the same
        self.assertEqual(imported_hive.current_player, self.hive.current_player)

        # Check if board is the same
        for hexagon, pieces in imported_hive.level.tiles.items():
            self.assertEqual(pieces, self.hive.level.get_tile_content(hexagon))

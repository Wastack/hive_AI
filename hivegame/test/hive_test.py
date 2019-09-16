from hivegame.hive import Hive, HiveException
from unittest import TestCase


from hivegame.pieces.ant_piece import AntPiece
from hivegame.pieces.beetle_piece import BeetlePiece
from hivegame.pieces.spider_piece import SpiderPiece
from hivegame.hive_utils import Direction, GameStatus, Player

import hivegame.hive_validation as valid
import hivegame.hive_representation as represent
from utils import hexutil
import logging
import sys

FORMAT = "[%(filename)s:%(lineno)s - %(funcName)20s() ] %(message)s"
logging.basicConfig(level=logging.DEBUG, format=FORMAT)
logger = logging.getLogger()


class TestHive(TestCase):
    """Verify the game logic"""

    def setUp(self):
        #                / \
        #               |bA1|
        #          / \   \ / \
        #         |wQ1|   |bQ1|
        #    / \   \ / \ / \ / \
        #   |wG1|   |wS1|bS1|bG1|
        #    \ / \ / \ / \ / \ /
        #     |wB1|wS2|   |bB1|
        #      \ / \ /     \ /

        self.hive = Hive()
        self.sh = logging.StreamHandler(sys.stdout)
        logger.addHandler(self.sh)

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

    def test_one_hive(self):
        self.assertFalse(valid.validate_one_hive(self.hive, self.hive.get_piece_by_name('wS1')))
        self.assertTrue(valid.validate_one_hive(self.hive, self.hive.get_piece_by_name('wQ1')))

    def test_one_hive_with_load_state(self):
        #for k,v in represent.get_adjacency_state(self.hive).items():
        #    print("{}: {}".format(k, v))
        #print(represent.two_dim_representation(represent.get_adjacency_state(self.hive)))
        hive = Hive.load_state_with_player(represent.two_dim_representation(represent.get_adjacency_state(self.hive)),
                                         self.hive.current_player)

        self.assertFalse(valid.validate_one_hive(hive, hive.get_piece_by_name('wS1')))
        self.assertTrue(valid.validate_one_hive(hive, hive.get_piece_by_name('wQ1')))

    def test_bee_moves(self):
        print(self.hive)
        bee_pos = self.hive.locate('wQ1')  # (-1, -1)
        expected = {hexutil.Hex(-2, 0), hexutil.Hex(1, -1)}
        self.assertEqual(expected, set(self.hive.bee_moves(bee_pos)))

        bee_pos = self.hive.locate('wS1')  # (0, 0)
        expected = []
        self.assertEqual(expected, self.hive.bee_moves(bee_pos))

        bee_pos = self.hive.locate('wS2')  # (-1, 1)
        expected = {hexutil.Hex(1, 1), hexutil.Hex(-2, 2)}
        self.assertEqual(expected, set(self.hive.bee_moves(bee_pos)))

    def test_ant_moves(self):
        end_cell = self.hive.poc2cell('wS1', Direction.HX_W)
        self.assertFalse(
            self.hive.get_piece_by_name('bA1').validate_move(self.hive, end_cell)
        )

        end_cell = self.hive.poc2cell('wS2', Direction.HX_SW)
        self.assertTrue(
            self.hive.get_piece_by_name('bA1').validate_move(self.hive, end_cell)
        )

        end_cell = self.hive.poc2cell('bA1', Direction.HX_SW)
        self.assertTrue(
            self.hive.get_piece_by_name('bA1').validate_move(self.hive, end_cell)
        )

        end_cell = self.hive.poc2cell('bS1', Direction.HX_SW)
        self.assertTrue(
            self.hive.get_piece_by_name('bA1').validate_move(self.hive, end_cell)
        )

        end_cell = self.hive.poc2cell('wS1', Direction.HX_NE)
        self.assertTrue(
            self.hive.get_piece_by_name('bA1').validate_move(self.hive, end_cell)
        )

        end_cell = self.hive.poc2cell('wQ1', Direction.HX_W)
        self.assertTrue(
            self.hive.get_piece_by_name('bA1').validate_move(self.hive, end_cell)
        )

    def test_beetle_moves(self):
        # moving in the ground level
        end_cell = self.hive.poc2cell('wS2', Direction.HX_E)
        self.assertTrue(
            self.hive.get_piece_by_name('bB1').validate_move(self.hive, end_cell)
        )

        self.hive.level.current_player = Player.WHITE
        self.hive.place_piece_without_action('wB2', 'wQ1', Direction.HX_W)
        end_cell = self.hive.poc2cell('wQ1', Direction.HX_SE)
        self.assertFalse(
            self.hive.get_piece_by_name('bB1').validate_move(self.hive, end_cell)
        )

        # moving from ground to top
        end_cell = self.hive.poc2cell('bS1', Direction.HX_O)
        self.assertTrue(
            self.hive.get_piece_by_name('bB1').validate_move(self.hive, end_cell)
        )

        # moving on top of the pieces
        self.hive.level.current_player = Player.BLACK
        self.hive.move_piece_without_action('bB1', 'bS1', Direction.HX_O)
        end_cell = self.hive.poc2cell('bS1', Direction.HX_E)
        self.assertTrue(
            self.hive.get_piece_by_name('bB1').validate_move(self.hive, end_cell)
        )

        self.hive.move_piece_without_action('bB1', 'bS1', Direction.HX_E)
        # Piece under beetle should be blocked
        end_cell = self.hive.poc2cell('bA1', Direction.HX_E)
        self.assertFalse(
            self.hive.get_piece_by_name('bG1').validate_move(self.hive, end_cell)
        )

        # moving from top to ground
        end_cell = self.hive.poc2cell('bG1', Direction.HX_E)
        self.assertTrue(
            self.hive.get_piece_by_name('bB1').validate_move(self.hive, end_cell)
        )

    def test_grasshopper_moves(self):
        end_cell = self.hive.poc2cell('wS1', Direction.HX_W)
        self.assertTrue(
            self.hive.get_piece_by_name('bG1').validate_move(self.hive, end_cell)
        )

        end_cell = self.hive.poc2cell('bA1', Direction.HX_NW)
        self.assertTrue(
            self.hive.get_piece_by_name('bG1').validate_move(self.hive, end_cell)
        )

        end_cell = self.hive.poc2cell('wG1', Direction.HX_W)
        self.assertFalse(
            self.hive.get_piece_by_name('bG1').validate_move(self.hive, end_cell)
        )

        end_cell = self.hive.poc2cell('wB1', Direction.HX_SE)
        self.assertTrue(
            self.hive.get_piece_by_name('wG1').validate_move(self.hive, end_cell)
        )

    def test_queen_moves(self):
        end_cell = self.hive.poc2cell('bQ1', Direction.HX_E)
        self.assertTrue(
            self.hive.get_piece_by_name('bQ1').validate_move(self.hive, end_cell)
        )

        end_cell = self.hive.poc2cell('bQ1', Direction.HX_W)
        self.assertFalse(
            self.hive.get_piece_by_name('bQ1').validate_move(self.hive, end_cell)
        )

        # moving out of a surrounding situation
        self.hive.level.current_player = Player.WHITE
        self.hive.move_piece_without_action('wQ1', 'wS1', Direction.HX_W)
        self.hive.level.current_player = Player.BLACK
        self.hive.move_piece_without_action('bA1', 'wG1', Direction.HX_NE)

        end_cell = self.hive.poc2cell('wS1', Direction.HX_NW)
        self.assertFalse(
            self.hive.get_piece_by_name('wQ1').validate_move(self.hive, end_cell)
        )

    def test_spider_moves(self):
        self.hive.place_piece_without_action('bS2', 'bA1', Direction.HX_NE)

        end_cell = self.hive.poc2cell('wQ1', Direction.HX_E)
        self.assertFalse(
            self.hive.get_piece_by_name('bS2').validate_move(self.hive, end_cell)
        )

        end_cell = self.hive.poc2cell('wQ1', Direction.HX_NW)
        self.assertTrue(
            self.hive.get_piece_by_name('bS2').validate_move(self.hive, end_cell)
        )

        end_cell = self.hive.poc2cell('wQ1', Direction.HX_W)
        self.assertFalse(
            self.hive.get_piece_by_name('bS2').validate_move(self.hive, end_cell)
        )

        end_cell = self.hive.poc2cell('bG1', Direction.HX_E)
        self.assertTrue(
            self.hive.get_piece_by_name('bS2').validate_move(self.hive, end_cell)
        )

        end_cell = self.hive.poc2cell('bA1', Direction.HX_E)
        self.assertFalse(
            self.hive.get_piece_by_name('bS2').validate_move(self.hive, end_cell)
        )

    def test_spider_moves2(self):
        self.hive.place_piece_without_action('bS2', 'bB1', Direction.HX_SE)

        end_cell = self.hive.poc2cell('wS2', Direction.HX_SE)
        self.assertTrue(
            self.hive.get_piece_by_name('bS2').validate_move(self.hive, end_cell)
        )

    def test_validate_place_piece(self):
        white_ant_1 = AntPiece('w', 1)
        black_beetle_2 = BeetlePiece('b', 2)

        # place over another piece
        cell = self.hive.poc2cell('wS1', Direction.HX_SW)
        self.assertFalse(
            valid.validate_place_piece(self.hive, white_ant_1, cell)
        )

        # valid placement
        cell = self.hive.poc2cell('bG1', Direction.HX_E)
        self.assertTrue(
            valid.validate_place_piece(self.hive, black_beetle_2, cell)
        )

        # wrong color
        cell = self.hive.poc2cell('wQ1', Direction.HX_E)
        self.assertFalse(
            valid.validate_place_piece(self.hive, white_ant_1, cell)
        )

    def test_move_piece(self):
        # move beetle over spider
        cell = self.hive.locate('bS1')
        self.hive.move_piece_without_action('bB1', 'bS1', Direction.HX_O)
        pieces = self.hive.level.get_tile_content(cell)
        self.assertEqual(cell, self.hive.locate('bB1'))
        self.assertEqual(2, len(pieces))
        self.assertTrue(BeetlePiece('b', 1) in pieces)
        self.assertTrue(SpiderPiece('b', 1) in pieces)

    def test_first_move(self):
        r"""Test that we can move a piece on the 3rd turn
        wA1, bA1/*wA1, wG1*|wA1, bS1/*bA1, wQ1\*wA1, bA2*\\bA1, wG1|*wA1
        """
        hive = Hive()

        hive.action_piece_to(AntPiece('w', 1), hexutil.origin)
        hive.action_piece_to(hive.get_piece_by_name('bA1'), hive.level.goto_direction(hexutil.origin, Direction.HX_SW))
        hive.action_piece_to(hive.get_piece_by_name('wG1'), hive.level.goto_direction(hive.locate('wA1'), Direction.HX_E))
        hive.action_piece_to(hive.get_piece_by_name('bS1'), hive.level.goto_direction(hive.locate('bA1'), Direction.HX_SW))
        hive.action_piece_to(hive.get_piece_by_name('wQ1'), hive.level.goto_direction(hive.locate('wA1'), Direction.HX_NW))
        hive.action_piece_to(hive.get_piece_by_name('bA2'), hive.level.goto_direction(hive.locate('bA1'), Direction.HX_SE))
        hive.action_piece_to(hive.get_piece_by_name('wG1'), hive.level.goto_direction(hive.locate('wA1'), Direction.HX_W))

    def test_fail_placement(self):
        """Test that we can place a piece after an incorrect try.
        wA1, bA1/*wA1, wG1|*bA1, wG1*|wA1
        """
        hive = Hive()

        hive.action_piece_to(AntPiece('w', 1), hexutil.origin)
        hive.action_piece_to(hive.get_piece_by_name('bA1'), hive.level.goto_direction(hexutil.origin, Direction.HX_SW))
        try:
            # This placement fails
            hive.action_piece_to(hive.get_piece_by_name('wG1'),
                                 hive.level.goto_direction(hive.locate('bA1'), Direction.HX_W))
        except HiveException:
            pass
        # This placement is correct
        hive.action_piece_to(hive.get_piece_by_name('wG1'), hive.level.goto_direction(hive.locate('wA1'), Direction.HX_E))

    def test_victory_conditions(self):
        """Test that we end the game when a victory/draw condition is meet."""
        hive = Hive()

        hive.action_piece_to(SpiderPiece('w', 1), hexutil.origin)
        hive.action_piece_to(SpiderPiece('b', 1), hive.level.goto_direction(hexutil.origin, Direction.HX_E))
        hive.action_piece_to(hive.get_piece_by_name('wQ1'), hive.level.goto_direction(hexutil.origin, Direction.HX_SW))
        hive.action_piece_to(hive.get_piece_by_name('bQ1'), hive.level.goto_direction(hive.locate('bS1'), Direction.HX_SE))
        hive.action_piece_to(hive.get_piece_by_name('wG1'), hive.level.goto_direction(hive.locate('wQ1'), Direction.HX_W))
        hive.action_piece_to(hive.get_piece_by_name('bS2'), hive.level.goto_direction(hive.locate('bS1'), Direction.HX_E))
        hive.action_piece_to(hive.get_piece_by_name('wA1'), hive.level.goto_direction(hive.locate('wQ1'), Direction.HX_SE))
        hive.action_piece_to(hive.get_piece_by_name('bA1'), hive.level.goto_direction(hive.locate('bQ1'), Direction.HX_E))
        hive.action_piece_to(hive.get_piece_by_name('wG1'), hive.level.goto_direction(hive.locate('wQ1'), Direction.HX_E))
        hive.action_piece_to(hive.get_piece_by_name('bG2'), hive.level.goto_direction(hive.locate('bQ1'), Direction.HX_SE))
        hive.action_piece_to(hive.get_piece_by_name('wA1'), hive.level.goto_direction(hive.locate('wG1'), Direction.HX_SE))

        self.assertTrue(hive.check_victory() == GameStatus.WHITE_WIN)


if __name__ == '__main__':
    import unittest
    unittest.main()

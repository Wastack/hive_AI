from hivegame.hive import Hive, HiveException
from unittest import TestCase


from hivegame.pieces.ant_piece import AntPiece
from hivegame.pieces.beetle_piece import BeetlePiece
from hivegame.pieces.spider_piece import SpiderPiece
from hivegame.hive_utils import Direction, GameStatus

import hivegame.hive_validation as valid
import hivegame.hive_representation as represent


class TestHive(TestCase):
    """Verify the game logic"""

    def setUp(self):
        #    / \ / \ / \ / \ / \
        #   |wB1|wS2|   |bB1|   |
        #  / \ / \ / \ / \ / \ /
        # |wG1|   |wS1|bS1|bG1|
        #  \ / \ / \ / \ / \ / \
        #   |   |wQ1|   |bQ1|   |
        #  / \ / \ / \ / \ / \ /
        # |   |   |   |bA1|   |
        #  \ / \ / \ / \ / \ /
        # next is black player turn
        #    / \ / \ / \ / \ / \
        #   |21-|11-|0-1|1-1|2-1|
        #  / \ / \ / \ / \ / \ /
        # |-20|-10|0,0|1,0|2,0|
        #  \ / \ / \ / \ / \ / \
        #   |-21|-11|0,1|1,1|2,1|
        #  / \ / \ / \ / \ / \ /
        # |-22|-12|0,2|1,2|2,2|
        #  \ / \ / \ / \ / \ /

        self.hive = Hive()
        self.hive.setup()

        self.hive.action('play', 'wS1')
        self.hive.action('play', ('bS1', 'wS1', Direction.HX_E))
        self.hive.action('play', ('wQ1', 'wS1', Direction.HX_SW))
        self.hive.action('play', ('bQ1', 'bS1', Direction.HX_SE))
        self.hive.action('play', ('wS2', 'wS1', Direction.HX_NW))
        self.hive.action('play', ('bG1', 'bS1', Direction.HX_E))
        self.hive.action('play', ('wB1', 'wS2', Direction.HX_W))
        self.hive.action('play', ('bA1', 'bQ1', Direction.HX_SW))
        self.hive.action('play', ('wG1', 'wB1', Direction.HX_SW))
        self.hive.place_piece_without_action(BeetlePiece('b', 1), 'bS1', Direction.HX_NE)

    def test_one_hive(self):
        self.assertFalse(valid.validate_one_hive(self.hive, self.hive.playedPieces['wS1']))
        self.assertTrue(valid.validate_one_hive(self.hive, self.hive.playedPieces['wQ1']))
        #print("[DEBUG] Action vector: ")
        #print(represent.get_all_action_vector(self.hive))

    def test_one_hive_with_load_state(self):
        self.hive.load_state((represent.get_adjacency_state(self.hive), self.hive.turn))
        print("[DEBUG] adjacency state:")
        print(represent.list_representation(represent.get_adjacency_state(self.hive)))
        self.assertFalse(valid.validate_one_hive(self.hive, self.hive.playedPieces['wS1']))
        self.assertTrue(valid.validate_one_hive(self.hive, self.hive.playedPieces['wQ1']))

    def test_bee_moves(self):
        bee_pos = self.hive.locate('wQ1')  # (-1, 1)
        expected = [(-1, 0), (0, 1)]
        self.assertEqual(expected, self.hive.bee_moves(bee_pos))

        bee_pos = self.hive.locate('wS1')
        expected = []
        self.assertEqual(expected, self.hive.bee_moves(bee_pos))

        bee_pos = self.hive.locate('wS2')
        expected = [(-1, -2), (0, -1)]
        self.assertEqual(expected, self.hive.bee_moves(bee_pos))

    def test_ant_moves(self):
        end_cell = self.hive.poc2cell('wS1', Direction.HX_W)
        self.assertFalse(
            self.hive.playedPieces['bA1'].validate_move(self.hive, end_cell)
        )

        end_cell = (-2, 2)
        self.assertFalse(
            self.hive.playedPieces['bA1'].validate_move(self.hive, end_cell)
        )

        end_cell = self.hive.poc2cell('bA1', Direction.HX_SW)
        self.assertFalse(
            self.hive.playedPieces['bA1'].validate_move(self.hive, end_cell)
        )

        end_cell = self.hive.poc2cell('bS1', Direction.HX_SW)
        self.assertTrue(
            self.hive.playedPieces['bA1'].validate_move(self.hive, end_cell)
        )

        end_cell = self.hive.poc2cell('wS1', Direction.HX_NE)
        self.assertTrue(
            self.hive.playedPieces['bA1'].validate_move(self.hive, end_cell)
        )

        end_cell = self.hive.poc2cell('wQ1', Direction.HX_W)
        self.assertTrue(
            self.hive.playedPieces['bA1'].validate_move(self.hive, end_cell)
        )

    def test_beetle_moves(self):
        # moving in the ground level
        end_cell = self.hive.poc2cell('wS2', Direction.HX_E)
        self.assertTrue(
            self.hive.playedPieces['bB1'].validate_move(self.hive, end_cell)
        )

        end_cell = self.hive.poc2cell('bB1', Direction.HX_NW)
        self.assertFalse(
            self.hive.playedPieces['bB1'].validate_move(self.hive, end_cell)
        )

        self.hive.set_turn(11)  # WHITE
        self.hive.place_piece_without_action(BeetlePiece('w', 2), 'wQ1', Direction.HX_W)
        end_cell = self.hive.poc2cell('wQ1', Direction.HX_NW)
        self.assertFalse(
            self.hive.playedPieces['bB1'].validate_move(self.hive, end_cell)
        )

        # moving from ground to top
        end_cell = self.hive.poc2cell('bS1', Direction.HX_O)
        self.assertTrue(
            self.hive.playedPieces['bB1'].validate_move(self.hive, end_cell)
        )

        # moving on top of the pieces
        self.hive.set_turn(12)  # BLACK
        beetle = self.hive.playedPieces['bB1']
        self.hive.move_piece_without_action(beetle, 'bS1', Direction.HX_O)
        end_cell = self.hive.poc2cell('bS1', Direction.HX_W)
        self.assertTrue(
            self.hive.playedPieces['bB1'].validate_move(self.hive, end_cell)
        )

        # moving from top to ground
        end_cell = self.hive.poc2cell('bS1', Direction.HX_W)
        self.assertTrue(
            self.hive.playedPieces['bB1'].validate_move(self.hive, end_cell)
        )

    def test_grasshopper_moves(self):
        end_cell = self.hive.poc2cell('wS1', Direction.HX_W)
        self.assertTrue(
            self.hive.playedPieces['bG1'].validate_move(self.hive, end_cell)
        )

        end_cell = self.hive.poc2cell('bA1', Direction.HX_SW)
        self.assertTrue(
            self.hive.playedPieces['bG1'].validate_move(self.hive, end_cell)
        )

        end_cell = self.hive.poc2cell('wG1', Direction.HX_W)
        self.assertFalse(
            self.hive.playedPieces['bG1'].validate_move(self.hive, end_cell)
        )

        end_cell = self.hive.poc2cell('wB1', Direction.HX_NE)
        self.assertTrue(
            self.hive.playedPieces['wG1'].validate_move(self.hive, end_cell)
        )

    def test_queen_moves(self):
        end_cell = self.hive.poc2cell('bQ1', Direction.HX_E)
        self.assertTrue(
            self.hive.playedPieces['bQ1'].validate_move(self.hive, end_cell)
        )

        end_cell = self.hive.poc2cell('bQ1', Direction.HX_SW)
        self.assertFalse(
            self.hive.playedPieces['bQ1'].validate_move(self.hive, end_cell)
        )

        # moving out of a surrounding situation
        self.hive.set_turn(11)  # WHITE
        self.hive.move_piece_without_action(self.hive.playedPieces['wQ1'], 'wS1', Direction.HX_W)
        self.hive.set_turn(12)  # BLACK
        self.hive.move_piece_without_action(self.hive.playedPieces['bA1'], 'wG1', Direction.HX_SE)

        end_cell = self.hive.poc2cell('wS1', Direction.HX_SW)
        self.assertFalse(
            self.hive.playedPieces['wQ1'].validate_move(self.hive, end_cell)
        )

    def test_spider_moves(self):
        self.hive.place_piece_without_action(SpiderPiece('b', 2), 'bA1', Direction.HX_SE)

        end_cell = self.hive.poc2cell('wQ1', Direction.HX_E)
        self.assertFalse(
            self.hive.playedPieces['bS2'].validate_move(self.hive, end_cell)
        )

        end_cell = self.hive.poc2cell('wQ1', Direction.HX_SW)
        self.assertTrue(
            self.hive.playedPieces['bS2'].validate_move(self.hive, end_cell)
        )

        end_cell = self.hive.poc2cell('wQ1', Direction.HX_W)
        self.assertFalse(
            self.hive.playedPieces['bS2'].validate_move(self.hive, end_cell)
        )

        end_cell = self.hive.poc2cell('bG1', Direction.HX_E)
        self.assertTrue(
            self.hive.playedPieces['bS2'].validate_move(self.hive, end_cell)
        )

        end_cell = self.hive.poc2cell('bA1', Direction.HX_E)
        self.assertFalse(
            self.hive.playedPieces['bS2'].validate_move(self.hive, end_cell)
        )

    def test_spider_moves2(self):
        spider = SpiderPiece('b', 2)
        self.hive.place_piece_without_action(spider, 'bB1', Direction.HX_NE)

        end_cell = self.hive.poc2cell('wS2', Direction.HX_NE)
        self.assertTrue(
            self.hive.playedPieces['bS2'].validate_move(self.hive, end_cell)
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
        black_beetle_1 = self.hive.playedPieces['bB1']
        cell = self.hive.locate('bS1')
        self.hive.move_piece_without_action(black_beetle_1, 'bS1', Direction.HX_O)
        pieces = self.hive.get_pieces(cell)

        self.assertEqual(cell, self.hive.locate('bB1'))
        self.assertEqual(2, len(pieces))
        self.assertTrue('bB1' in pieces)
        self.assertTrue('bS1' in pieces)

    def test_action(self):
        """ place a piece and verify unplayed_pieces dict """
        self.hive.action('play', ('bS2', 'bQ1', Direction.HX_E))
        unplayed_pieces = self.hive.get_unplayed_pieces('b')

        self.assertFalse('bS2' in unplayed_pieces)

    def test_first_move(self):
        r"""Test that we can move a piece on the 3rd turn
        wA1, bA1/*wA1, wG1*|wA1, bS1/*bA1, wQ1\*wA1, bA2*\\bA1, wG1|*wA1
        """
        hive = Hive()
        hive.setup()

        hive.action('play', 'wA1')
        hive.action('play', ('bA1', 'wA1', Direction.HX_NW))
        hive.action('play', ('wG1', 'wA1', Direction.HX_E))
        hive.action('play', ('bS1', 'bA1', Direction.HX_NW))
        hive.action('play', ('wQ1', 'wA1', Direction.HX_SW))
        hive.action('play', ('bA2', 'bA1', Direction.HX_NE))
        hive.action('play', ('wG1', 'wA1', Direction.HX_W))

    def test_fail_placement(self):
        """Test that we can place a piece after an incorrect try.
        wA1, bA1/*wA1, wG1|*bA1, wG1*|wA1
        """
        hive = Hive()
        hive.setup()

        hive.action('play', 'wA1')
        hive.action('play', ('bA1', 'wA1', Direction.HX_NW))
        try:
            # This placement fails
            hive.action('play', ('wG1', 'bA1', Direction.HX_W))
        except HiveException:
            pass
        # This placement is correct
        hive.action('play', ('wG1', 'wA1', Direction.HX_E))

    def test_victory_conditions(self):
        """Test that we end the game when a victory/draw condition is meet."""
        hive = Hive()
        hive.setup()

        hive.action('play', 'wS1')
        hive.action('play', ('bS1', 'wS1', Direction.HX_E))
        hive.action('play', ('wQ1', 'wS1', Direction.HX_NW))
        hive.action('play', ('bQ1', 'bS1', Direction.HX_NE))
        hive.action('play', ('wG1', 'wQ1', Direction.HX_W))
        hive.action('play', ('bS2', 'bS1', Direction.HX_E))
        hive.action('play', ('wA1', 'wQ1', Direction.HX_NE))
        hive.action('play', ('bA1', 'bQ1', Direction.HX_E))
        hive.action('play', ('wG1', 'wQ1', Direction.HX_E))
        hive.action('play', ('bG2', 'bQ1', Direction.HX_NE))
        hive.action('play', ('wA1', 'wG1', Direction.HX_NE))

        self.assertTrue(hive.check_victory() == GameStatus.WHITE_WIN)


if __name__ == '__main__':
    import unittest
    unittest.main()

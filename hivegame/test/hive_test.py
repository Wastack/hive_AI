from hivegame.hive import Hive
from unittest import TestCase

from hivegame.view import HiveView

from hivegame.pieces.ant_piece import AntPiece
from hivegame.pieces.bee_piece import BeePiece
from hivegame.pieces.beetle_piece import BeetlePiece
from hivegame.pieces.grasshopper_piece import GrassHopperPiece
from hivegame.pieces.spider_piece import SpiderPiece
from hivegame.pieces.piece import HivePiece

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

        self.hive = Hive()
        self.hive.setup()

        self.hive.action('play', ('wS1'))
        self.hive.action('play', ('bS1', 'wS1', self.hive.E))
        self.hive.action('play', ('wQ1', 'wS1', self.hive.SW))
        self.hive.action('play', ('bQ1', 'bS1', self.hive.SE))
        self.hive.action('play', ('wS2', 'wS1', self.hive.NW))
        self.hive.action('play', ('bG1', 'bS1', self.hive.E))
        self.hive.action('play', ('wB1', 'wS2', self.hive.W))
        self.hive.action('play', ('bA1', 'bQ1', self.hive.SW))
        self.hive.action('play', ('wG1', 'wB1', self.hive.SW))
        self.hive.place_piece(BeetlePiece('b', 1), 'bS1', self.hive.NE)


    def test_one_hive(self):
        self.assertFalse(self.hive._one_hive(self.hive.playedPieces['wS1']))
        self.assertTrue(self.hive._one_hive(self.hive.playedPieces['wQ1']))


    def testbee_moves(self):
        beePos = self.hive.locate('wQ1')  # (-1, 1)
        expected = [(-1, 0), (0, 1)]
        self.assertEqual(expected, self.hive.bee_moves(beePos))

        beePos = self.hive.locate('wS1')
        expected = []
        self.assertEqual(expected, self.hive.bee_moves(beePos))

        beePos = self.hive.locate('wS2')
        expected = [(-1, -2), (0, -1)]
        self.assertEqual(expected, self.hive.bee_moves(beePos))


    def test_ant_moves(self):
        endCell = self.hive._poc2cell('wS1', self.hive.W)
        self.assertFalse(
            self.hive.playedPieces['bA1'].validate_move(self.hive, endCell)
        )

        endCell = (-2, 2)
        self.assertFalse(
            self.hive.playedPieces['bA1'].validate_move(self.hive, endCell)
        )

        endCell = self.hive._poc2cell('bA1', self.hive.SW)
        self.assertFalse(
            self.hive.playedPieces['bA1'].validate_move(self.hive, endCell)
        )

        endCell = self.hive._poc2cell('bS1', self.hive.SW)
        self.assertTrue(
            self.hive.playedPieces['bA1'].validate_move(self.hive, endCell)
        )

        endCell = self.hive._poc2cell('wS1', self.hive.NE)
        self.assertTrue(
            self.hive.playedPieces['bA1'].validate_move(self.hive, endCell)
        )

        endCell = self.hive._poc2cell('wQ1', self.hive.W)
        self.assertTrue(
            self.hive.playedPieces['bA1'].validate_move(self.hive, endCell)
        )


    def test_beetle_moves(self):
        # moving in the ground level
        endCell = self.hive._poc2cell('wS2', self.hive.E)
        self.assertTrue(
            self.hive.playedPieces['bB1'].validate_move(self.hive, endCell)
        )

        endCell = self.hive._poc2cell('bB1', self.hive.NW)
        self.assertFalse(
            self.hive.playedPieces['bB1'].validate_move(self.hive, endCell)
        )

        self.hive.turn = 11  # set turn to be white player turn
        self.hive.activePlayer = 0
        self.hive.place_piece(BeetlePiece('w', 2), 'wQ1', self.hive.W)
        endCell = self.hive._poc2cell('wQ1', self.hive.NW)
        self.assertFalse(
            self.hive.playedPieces['bB1'].validate_move(self.hive, endCell)
        )

        # moving from ground to top
        endCell = self.hive._poc2cell('bS1', self.hive.O)
        self.assertTrue(
            self.hive.playedPieces['bB1'].validate_move(self.hive, endCell)
        )

        # moving on top of the pieces
        self.hive.turn = 12  # set turn to be black player turn
        self.hive.activePlayer = 1
        beetle = self.hive.playedPieces['bB1']
        self.hive.move_piece(beetle, 'bS1', self.hive.O)
        endCell = self.hive._poc2cell('bS1', self.hive.W)
        self.assertTrue(
            self.hive.playedPieces['bB1'].validate_move(self.hive, endCell)
        )

        # moving from top to ground
        endCell = self.hive._poc2cell('bS1', self.hive.SW)
        self.assertTrue(
            self.hive.playedPieces['bB1'].validate_move(self.hive, endCell)
        )


    def test_grasshopper_moves(self):
        endCell = self.hive._poc2cell('wS1', self.hive.W)
        self.assertTrue(
            self.hive.playedPieces['bG1'].validate_move(self.hive, endCell)
        )

        endCell = self.hive._poc2cell('bA1', self.hive.SW)
        self.assertTrue(
            self.hive.playedPieces['bG1'].validate_move(self.hive, endCell)
        )

        endCell = self.hive._poc2cell('wG1', self.hive.W)
        self.assertFalse(
            self.hive.playedPieces['bG1'].validate_move(self.hive, endCell)
        )

        endCell = self.hive._poc2cell('wB1', self.hive.NE)
        self.assertTrue(
            self.hive.playedPieces['wG1'].validate_move(self.hive, endCell)
        )


    def test_queen_moves(self):
        endCell = self.hive._poc2cell('bQ1', self.hive.E)
        self.assertTrue(
            self.hive.playedPieces['bQ1'].validate_move(self.hive, endCell)
        )

        endCell = self.hive._poc2cell('bQ1', self.hive.SW)
        self.assertFalse(
            self.hive.playedPieces['bQ1'].validate_move(self.hive, endCell)
        )

        # moving out of a surrounding situation
        self.hive.turn = 11  # set turn to be white player turn
        self.hive.activePlayer = 0
        self.hive.move_piece(self.hive.playedPieces['wQ1'], 'wS1', self.hive.W)
        self.hive.turn = 12  # set turn to be black player turn
        self.hive.activePlayer = 1
        self.hive.move_piece(self.hive.playedPieces['bA1'], 'wG1', self.hive.SE)

        endCell = self.hive._poc2cell('wS1', self.hive.SW)
        self.assertFalse(
            self.hive.playedPieces['wQ1'].validate_move(self.hive, endCell)
        )


    def test_spider_moves(self):
        self.hive.place_piece(SpiderPiece('b', 2), 'bA1', self.hive.SE)

        endCell = self.hive._poc2cell('wQ1', self.hive.E)
        self.assertFalse(
            self.hive.playedPieces['bS2'].validate_move(self.hive, endCell)
        )

        endCell = self.hive._poc2cell('wQ1', self.hive.SW)
        self.assertTrue(
            self.hive.playedPieces['bS2'].validate_move(self.hive, endCell)
        )

        endCell = self.hive._poc2cell('wQ1', self.hive.W)
        self.assertFalse(
            self.hive.playedPieces['bS2'].validate_move(self.hive, endCell)
        )

        endCell = self.hive._poc2cell('bG1', self.hive.E)
        self.assertTrue(
            self.hive.playedPieces['bS2'].validate_move(self.hive, endCell)
        )

        endCell = self.hive._poc2cell('bA1', self.hive.E)
        self.assertFalse(
            self.hive.playedPieces['bS2'].validate_move(self.hive, endCell)
        )


    def test_spider_moves2(self):
        spider = SpiderPiece('b', 2)
        self.hive.place_piece(spider, 'bB1', self.hive.NE)

        endCell = self.hive._poc2cell('wS2', self.hive.NE)
        self.assertTrue(
            self.hive.playedPieces['bS2'].validate_move(self.hive, endCell)
        )


    def test_validate_place_piece(self):
        wA1 = AntPiece('w', 1)
        bB2 = BeetlePiece('b', 2)

        # place over another piece
        cell = self.hive._poc2cell('wS1', self.hive.SW)
        self.assertFalse(
            self.hive._validate_place_piece(wA1, cell)
        )

        # valid placement
        cell = self.hive._poc2cell('bG1', self.hive.E)
        self.assertTrue(
            self.hive._validate_place_piece(bB2, cell)
        )

        # wrong color
        cell = self.hive._poc2cell('wQ1', self.hive.E)
        self.assertFalse(
            self.hive._validate_place_piece(wA1, cell)
        )


    def test_move_piece(self):
        # move beetle over spider
        bB1 = self.hive.playedPieces['bB1']
        cell = self.hive.locate('bS1')
        self.hive.move_piece(bB1, 'bS1', self.hive.O)
        pieces = self.hive.get_pieces(cell)

        self.assertEqual(cell, self.hive.locate('bB1'))
        self.assertEqual(2, len(pieces))
        self.assertTrue('bB1' in pieces)
        self.assertTrue('bS1' in pieces)


    def test_action(self):
        # place a piece and verify unplayedPieces dict
        self.hive.action('play', ('bS2', 'bQ1', self.hive.E))
        unplayedPieces = self.hive.get_unplayed_pieces('b')

        self.assertFalse('bS2' in unplayedPieces)


    def test_first_move(self):
        r"""Test that we can move a piece on the 3rd turn
        wA1, bA1/*wA1, wG1*|wA1, bS1/*bA1, wQ1\*wA1, bA2*\\bA1, wG1|*wA1
        """
        hive = Hive()
        hive.setup()

        hive.action('play', ('wA1'))
        hive.action('play', ('bA1', 'wA1', hive.NW))
        hive.action('play', ('wG1', 'wA1', hive.E))
        hive.action('play', ('bS1', 'bA1', hive.NW))
        hive.action('play', ('wQ1', 'wA1', hive.SW))
        hive.action('play', ('bA2', 'bA1', hive.NE))
        hive.action('play', ('wG1', 'wA1', hive.W))


    def test_fail_placement(self):
        """Test that we can place a piece after an incorrect try.
        wA1, bA1/*wA1, wG1|*bA1, wG1*|wA1
        """
        hive = Hive()
        hive.setup()

        hive.action('play', ('wA1'))
        hive.action('play', ('bA1', 'wA1', hive.NW))
        try:
            # This placement fails
            hive.action('play', ('wG1', 'bA1', hive.W))
        except:
            pass
        # This placement is correct
        hive.action('play', ('wG1', 'wA1', hive.E))


    def test_victory_conditions(self):
        """Test that we end the game when a victory/draw condition is meet."""
        hive = Hive()
        hive.setup()

        hive.action('play', ('wS1'))
        hive.action('play', ('bS1', 'wS1', hive.E))
        hive.action('play', ('wQ1', 'wS1', hive.NW))
        hive.action('play', ('bQ1', 'bS1', hive.NE))
        hive.action('play', ('wG1', 'wQ1', hive.W))
        hive.action('play', ('bS2', 'bS1', hive.E))
        hive.action('play', ('wA1', 'wQ1', hive.NE))
        hive.action('play', ('bA1', 'bQ1', hive.E))
        hive.action('play', ('wG1', 'wQ1', hive.E))
        hive.action('play', ('bG2', 'bQ1', hive.NE))
        hive.action('play', ('wA1', 'wG1', hive.NE))

        self.assertTrue(hive.check_victory() == hive.WHITE_WIN)


if __name__ == '__main__':
    import unittest
    unittest.main()

from hivegame.hive import Hive
from hivegame.piece import HivePiece
from unittest import TestCase

from hivegame.view import HiveView


class TestHive(TestCase):
    """Verify the game logic"""

    # Pieces used for testing
    piece = {
        'wQ1': HivePiece('w', 'Q', 1),
        'wS1': HivePiece('w', 'S', 1),
        'wS2': HivePiece('w', 'S', 2),
        'wB1': HivePiece('w', 'B', 1),
        'wB2': HivePiece('w', 'B', 2),
        'wG1': HivePiece('w', 'G', 1),
        'bS1': HivePiece('b', 'S', 1),
        'bS2': HivePiece('b', 'S', 2),
        'bQ1': HivePiece('b', 'Q', 1),
        'bB1': HivePiece('b', 'B', 1),
        'bA1': HivePiece('b', 'A', 1),
        'bG1': HivePiece('b', 'G', 1),
    }

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
        self.hive.place_piece(self.piece['bB1'], 'bS1', self.hive.NE)

        view = HiveView(self.hive)
        view.print_pieces_with_coords()


    def test_one_hive(self):
        self.assertFalse(self.hive._one_hive(self.piece['wS1']))
        self.assertTrue(self.hive._one_hive(self.piece['wQ1']))


    def test_bee_moves(self):
        beePos = self.hive.locate('wQ1')  # (-1, 1)
        expected = [(-1, 0), (0, 1)]
        self.assertEqual(expected, self.hive._bee_moves(beePos))

        beePos = self.hive.locate('wS1')
        expected = []
        self.assertEqual(expected, self.hive._bee_moves(beePos))

        beePos = self.hive.locate('wS2')
        expected = [(-1, -2), (0, -1)]
        self.assertEqual(expected, self.hive._bee_moves(beePos))


    def test_ant_moves(self):
        startCell = self.hive.locate('bA1')
        endCell = self.hive._poc2cell('wS1', self.hive.W)
        self.assertFalse(
            self.hive._valid_ant_move(self.piece['bA1'], startCell, endCell)
        )

        endCell = (-2, 2)
        self.assertFalse(
            self.hive._valid_ant_move(self.piece['bA1'], startCell, endCell)
        )

        endCell = self.hive._poc2cell('bA1', self.hive.SW)
        self.assertFalse(
            self.hive._valid_ant_move(self.piece['bA1'], startCell, endCell)
        )

        endCell = self.hive._poc2cell('bS1', self.hive.SW)
        self.assertTrue(
            self.hive._valid_ant_move(self.piece['bA1'], startCell, endCell)
        )

        endCell = self.hive._poc2cell('wS1', self.hive.NE)
        self.assertTrue(
            self.hive._valid_ant_move(self.piece['bA1'], startCell, endCell)
        )

        endCell = self.hive._poc2cell('wQ1', self.hive.W)
        self.assertTrue(
            self.hive._valid_ant_move(self.piece['bA1'], startCell, endCell)
        )


    def test_beetle_moves(self):
        # moving in the ground level
        beetle = self.piece['bB1']
        startCell = self.hive.locate('bB1')
        endCell = self.hive._poc2cell('wS2', self.hive.E)
        self.assertTrue(
            self.hive._valid_beetle_move(beetle, startCell, endCell)
        )

        endCell = self.hive._poc2cell('bB1', self.hive.NW)
        self.assertFalse(
            self.hive._valid_beetle_move(beetle, startCell, endCell)
        )

        self.hive.turn = 11  # set turn to be white player turn
        self.hive.activePlayer = 0
        beetle = self.piece['wB2']
        self.hive.place_piece(beetle, 'wQ1', self.hive.W)
        startCell = self.hive._poc2cell('wQ1', self.hive.W)
        endCell = self.hive._poc2cell('wQ1', self.hive.NW)
        self.assertFalse(
            self.hive._valid_beetle_move(beetle, startCell, endCell)
        )

        # moving from ground to top
        beetle = self.piece['bB1']
        startCell = self.hive.locate('bB1')
        endCell = self.hive._poc2cell('bS1', self.hive.O)
        self.assertTrue(
            self.hive._valid_beetle_move(beetle, startCell, endCell)
        )

        # moving on top of the pieces
        self.hive.turn = 12  # set turn to be black player turn
        self.hive.activePlayer = 1
        beetle = self.piece['bB1']
        self.hive.move_piece(beetle, 'bS1', self.hive.O)
        startCell = self.hive.locate('bB1')
        endCell = self.hive._poc2cell('bS1', self.hive.W)
        self.assertTrue(
            self.hive._valid_beetle_move(beetle, startCell, endCell)
        )

        # moving from top to ground
        startCell = self.hive.locate('bB1')
        endCell = self.hive._poc2cell('bS1', self.hive.SW)
        self.assertTrue(
            self.hive._valid_beetle_move(beetle, startCell, endCell)
        )


    def test_grasshopper_moves(self):
        grasshopper = self.piece['bG1']
        startCell = self.hive.locate('bG1')
        endCell = self.hive._poc2cell('wS1', self.hive.W)
        self.assertTrue(
            self.hive._valid_grasshopper_move(grasshopper, startCell, endCell)
        )

        endCell = self.hive._poc2cell('bA1', self.hive.SW)
        self.assertTrue(
            self.hive._valid_grasshopper_move(grasshopper, startCell, endCell)
        )

        endCell = self.hive._poc2cell('wG1', self.hive.W)
        self.assertFalse(
            self.hive._valid_grasshopper_move(grasshopper, startCell, endCell)
        )

        grasshopper = self.piece['wG1']
        startCell = self.hive.locate('wG1')
        endCell = self.hive._poc2cell('wB1', self.hive.NE)
        self.assertTrue(
            self.hive._valid_grasshopper_move(grasshopper, startCell, endCell)
        )


    def test_queen_moves(self):
        queen = self.piece['bQ1']
        startCell = self.hive.locate('bQ1')
        endCell = self.hive._poc2cell('bQ1', self.hive.E)
        self.assertTrue(
            self.hive._valid_queen_move(queen, startCell, endCell)
        )

        endCell = self.hive._poc2cell('bQ1', self.hive.SW)
        self.assertFalse(
            self.hive._valid_queen_move(queen, startCell, endCell)
        )

        # moving out of a surrounding situation
        queen = self.piece['wQ1']
        bA1 = self.piece['bA1']
        self.hive.turn = 11  # set turn to be white player turn
        self.hive.activePlayer = 0
        self.hive.move_piece(queen, 'wS1', self.hive.W)
        self.hive.turn = 12  # set turn to be black player turn
        self.hive.activePlayer = 1
        self.hive.move_piece(bA1, 'wG1', self.hive.SE)

        startCell = self.hive.locate('wQ1')
        endCell = self.hive._poc2cell('wS1', self.hive.SW)
        self.assertFalse(
            self.hive._valid_queen_move(queen, startCell, endCell)
        )


    def test_spider_moves(self):
        spider = self.piece['bS2']
        self.hive.place_piece(spider, 'bA1', self.hive.SE)

        startCell = self.hive.locate('bS2')
        endCell = self.hive._poc2cell('wQ1', self.hive.E)
        self.assertFalse(
            self.hive._valid_spider_move(spider, startCell, endCell)
        )

        endCell = self.hive._poc2cell('wQ1', self.hive.SW)
        self.assertTrue(
            self.hive._valid_spider_move(spider, startCell, endCell)
        )

        endCell = self.hive._poc2cell('wQ1', self.hive.W)
        self.assertFalse(
            self.hive._valid_spider_move(spider, startCell, endCell)
        )

        endCell = self.hive._poc2cell('bG1', self.hive.E)
        self.assertTrue(
            self.hive._valid_spider_move(spider, startCell, endCell)
        )

        endCell = self.hive._poc2cell('bA1', self.hive.E)
        self.assertFalse(
            self.hive._valid_spider_move(spider, startCell, endCell)
        )


    def test_spider_moves2(self):
        spider = self.piece['bS2']
        self.hive.place_piece(spider, 'bB1', self.hive.NE)

        startCell = self.hive.locate('bS2')
        endCell = self.hive._poc2cell('wS2', self.hive.NE)
        self.assertTrue(
            self.hive._valid_spider_move(spider, startCell, endCell)
        )


    def test_validate_place_piece(self):
        wA1 = HivePiece('w', 'A', 1)
        bB2 = HivePiece('b', 'B', 2)

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
        bB1 = self.piece['bB1']
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
        """Test that we can move a piece on the 3rd turn
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

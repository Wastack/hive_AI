from hivegame.hive import Hive
import hivegame.hive_representation as represent
from unittest import TestCase
from hivegame.hive_utils import Player, Direction

import numpy as np

BUG_C = 22  # number of bugs without extension

import json

class TestRepresentation(TestCase):
    """
    Verify logic related to various outputs and inputs of the
    Hive engine.
    """

    @property
    def _list_repr(self):
        #    / \ / \ / \ / \ / \
        #   |wB1|wS2|   |bB1|   |
        #  / \ / \ / \ / \ / \ /
        # |wG1|   |wS1|bS1|bG1|
        #  \ / \ / \ / \ / \ / \
        #   |   |wQ1|   |bQ1|   |
        #  / \ / \ / \ / \ / \ /
        # |   |   |   |bA1|   |
        #  \ / \ / \ / \ / \ /

        with open('repr_data.json') as f:
            d = json.load(f)
            return np.array(d["repr_list"])

    def setUp(self) -> None:
        self.hive = Hive()
        self.hive.setup()
        pass

    def test_empty_adjacency_state(self):
        adj = represent.get_adjacency_state(self.hive)
        self.assertEqual(len(adj), BUG_C)
        self.assertEqual(len(adj.get(list(adj.keys())[0])), BUG_C - 1)

        list_repr = represent.list_representation(adj)
        self.assertEqual(len(list_repr), BUG_C*(BUG_C - 1))
        self.assertTrue(all(v == 0 for v in list_repr))

    def test_load_state_from_list(self):
        """Verify canonical adjacency state loading"""
        input_list = self._list_repr

        self.hive.load_state_with_player(input_list, Player.WHITE)
        # ['wS2', 'wB1', 'wS1', 'wG1', 'bS1', 'bB1', 'bQ1', 'wQ1', 'bG1', 'bA1']
        self.assertEqual(self.hive.played_piece_count(), 10)
        self.assertEqual(len(self.hive.unplayedPieces[Player.WHITE]), 6)
        self.assertEqual(len(self.hive.unplayedPieces[Player.BLACK]), 6)

        self.assertTrue("wS2" in self.hive.playedPieces.keys())
        self.assertTrue("wB1" in self.hive.playedPieces.keys())
        self.assertTrue("wS1" in self.hive.playedPieces.keys())
        self.assertTrue("wG1" in self.hive.playedPieces.keys())
        self.assertTrue("bS1" in self.hive.playedPieces.keys())
        self.assertTrue("bB1" in self.hive.playedPieces.keys())
        self.assertTrue("bQ1" in self.hive.playedPieces.keys())
        self.assertTrue("wQ1" in self.hive.playedPieces.keys())
        self.assertTrue("bG1" in self.hive.playedPieces.keys())
        self.assertTrue("bA1" in self.hive.playedPieces.keys())

        wB1_pos = self.hive.board.get_dir_cell(self.hive.playedPieces["wG1"].position, Direction.HX_NE)
        self.assertEqual(self.hive.playedPieces["wB1"].position, wB1_pos)

        # Verify everything around bS1
        bS1_pos = self.hive.playedPieces["bS1"].position
        self.assertEqual(self.hive.playedPieces["wS1"].position, self.hive.board.get_dir_cell(bS1_pos, Direction.HX_W))
        self.assertEqual(self.hive.playedPieces["bB1"].position, self.hive.board.get_dir_cell(bS1_pos, Direction.HX_NE))
        self.assertEqual(self.hive.playedPieces["bG1"].position, self.hive.board.get_dir_cell(bS1_pos, Direction.HX_E))
        self.assertEqual(self.hive.playedPieces["bQ1"].position, self.hive.board.get_dir_cell(bS1_pos, Direction.HX_SE))

        self.assertTrue(self.hive.is_cell_free(self.hive.board.get_dir_cell(bS1_pos, Direction.HX_NW)))
        self.assertTrue(self.hive.is_cell_free(self.hive.board.get_dir_cell(bS1_pos, Direction.HX_SW)))

        # Test transforming it back to the list representation
        np.testing.assert_equal(represent.two_dim_representation(represent.get_adjacency_state(self.hive)), input_list)

    def test_action_vector(self):
        self.hive.load_state_with_player(self._list_repr, Player.WHITE)

        with open('repr_data.json') as f:
            d = json.load(f)
            assert represent.get_all_action_vector(self.hive) == d["test_action_vector"]

    def test_actions_from_vector(self):
        self.hive.load_state_with_player(self._list_repr, Player.WHITE)
        all_actions = represent.get_all_action_vector(self.hive)
        print("[DEBUG] action vector: {}".format(all_actions))
        indices = [i for i, v in enumerate(all_actions) if v > 0]
        for action_number in indices:
            self.hive.action_from_vector(action_number)


if __name__ == '__main__':
    import unittest
    unittest.main()

from hivegame.hive import Hive
import hivegame.hive_representation as represent
from unittest import TestCase
from hivegame.hive_utils import Player, Direction
import numpy as np
import os
import json, sys

from hivegame.utils import hexutil

BUG_C = 22  # number of bugs without extension
import logging

FORMAT = "[%(filename)s:%(lineno)s - %(funcName)20s() ] %(message)s"
logging.basicConfig(level=logging.DEBUG, format=FORMAT)
logger = logging.getLogger()

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
        __location__ = os.path.realpath(
            os.path.join(os.getcwd(), os.path.dirname(__file__)))
        with open(os.path.join(__location__, 'repr_data.json')) as f:
            d = json.load(f)
            return np.array(d["repr_list"])

    def setUp(self) -> None:
        self.sh = logging.StreamHandler(sys.stdout)
        logger.addHandler(self.sh)
        self.hive = Hive()
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

        self.hive = Hive.load_state_with_player(input_list, Player.WHITE)
        # ['wS2', 'wB1', 'wS1', 'wG1', 'bS1', 'bB1', 'bQ1', 'wQ1', 'bG1', 'bA1']
        self.assertEqual(len(self.hive.level.get_played_pieces()), 10)
        self.assertEqual(len(self.hive.level.get_unplayed_pieces(Player.WHITE)), 6)
        self.assertEqual(len(self.hive.level.get_unplayed_pieces(Player.BLACK)), 6)

        names = [str(p) for p in self.hive.level.get_played_pieces()]
        self.assertTrue("wS2" in names)
        self.assertTrue("wB1" in names)
        self.assertTrue("wS1" in names)
        self.assertTrue("wG1" in names)
        self.assertTrue("bS1" in names)
        self.assertTrue("bB1" in names)
        self.assertTrue("bQ1" in names)
        self.assertTrue("wQ1" in names)
        self.assertTrue("bG1" in names)
        self.assertTrue("bA1" in names)

        wB1_pos = self.hive.level.goto_direction(self.hive.locate("wG1"), Direction.HX_NE)
        self.assertEqual(self.hive.locate("wB1"), wB1_pos)

        # Verify everything around bS1
        bS1_pos = self.hive.locate("bS1")
        self.assertEqual(self.hive.locate("wS1"), self.hive.level.goto_direction(bS1_pos, Direction.HX_W))
        self.assertEqual(self.hive.locate("bB1"), self.hive.level.goto_direction(bS1_pos, Direction.HX_NE))
        self.assertEqual(self.hive.locate("bG1"), self.hive.level.goto_direction(bS1_pos, Direction.HX_E))
        self.assertEqual(self.hive.locate("bQ1"), self.hive.level.goto_direction(bS1_pos, Direction.HX_SE))

        self.assertFalse(self.hive.level.get_tile_content(self.hive.level.goto_direction(bS1_pos, Direction.HX_NW)))
        self.assertFalse(self.hive.level.get_tile_content(self.hive.level.goto_direction(bS1_pos, Direction.HX_SW)))

        # Test transforming it back to the list representation
        result = represent.two_dim_representation(represent.get_adjacency_state(self.hive))
        np.testing.assert_equal(result, input_list)

    def test_action_vector(self):
        self.hive = Hive.load_state_with_player(self._list_repr, Player.WHITE)
        __location__ = os.path.realpath(
            os.path.join(os.getcwd(), os.path.dirname(__file__)))
        with open(os.path.join(__location__, 'repr_data.json')) as f:
            print(self.hive)
            d = json.load(f)
            res = represent.get_all_action_vector(self.hive)
            print(res)
            assert all([a == b for a,b in zip(res, d["test_action_vector"])])

    def test_actions_from_vector(self):
        self.hive = Hive.load_state_with_player(self._list_repr, Player.WHITE)
        all_actions = represent.get_all_action_vector(self.hive)
        indices = [i for i, v in enumerate(all_actions) if v > 0]
        for action_number in indices:
            self.hive.action_from_vector(action_number)

        # test other player's turn
        self.hive._toggle_player(self.hive.current_player)
        all_actions = represent.get_all_action_vector(self.hive)
        indices = [i for i, v in enumerate(all_actions) if v > 0]
        for action_number in indices:
            self.hive.action_from_vector(action_number)

    def test_action_numbers(self):
        self.hive = Hive()
        self.hive.place_piece_without_action("wB2")
        self.hive.level.current_player = Player.BLACK
        self.hive.place_piece_without_action("bB1", "wB2", Direction.HX_W)
        self.hive.level.current_player = Player.WHITE
        self.hive.place_piece_without_action("wA2", "wB2", Direction.HX_SE)
        self.hive.level.current_player = Player.BLACK
        self.hive.place_piece_without_action("bS2", "bB1", Direction.HX_W)
        self.hive.level.current_player = Player.WHITE
        self.assertEqual(represent.get_all_action_vector(self.hive)[90], 0)
        piece, end_cell = self.hive.action_from_vector(90)
        self.assertEqual(piece, self.hive.get_piece_by_name("wA2"))
        self.assertEqual(end_cell, hexutil.Hex(1, -1))
        logging.debug(self.hive)


if __name__ == '__main__':
    import unittest
    unittest.main()

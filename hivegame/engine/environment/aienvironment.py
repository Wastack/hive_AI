#! /usr/bin/env python

from typing import List

import engine.hive
from engine.hive_utils import GameStatus, Player
from engine.environment.AIGameEnv import AIGameEnv

import logging
import engine.hive_representation as represent
import utils.importexport

class AIEnvironment(AIGameEnv):
    """
    Environment controls the game. It contains all the methods to
    create a game, move or put down pieces, ask information about
    current state etc. This interface is stateless.
    """

    @staticmethod
    def pass_turn(hive):
        hive.pass_turn()


    @staticmethod
    def _player_to_inner_player(player_num):
        assert player_num == 1 or player_num == -1
        return Player.WHITE if player_num == 1 else Player.BLACK

# Methods for Game.py interface
    @staticmethod
    def string_representation(board):
        return represent.string_representation(board)

    @staticmethod
    def get_action_size():
        """
        :return: Number of possible actions in the given state
        """
        hive = engine.hive.Hive()
        return len(represent.get_all_action_vector(hive))

    @staticmethod
    def get_canonical_form(two_dim_repr: List[List[int]], player_num):
        hive = represent.load_state_with_player(two_dim_repr, AIEnvironment._player_to_inner_player(player_num))
        return represent.two_dim_representation(represent.canonical_adjacency_state(hive))

    @staticmethod
    def get_game_ended(board, player_num):
        # TODO victory condition should be configurable
        return AIEnvironment.get_game_ended_simplified(board, player_num)

    @staticmethod
    def get_game_ended_simplified(board, player):
        inner_player = AIEnvironment._player_to_inner_player(player)
        hive = represent.load_state_with_player(board, inner_player)
        res = 0
        white_queen_pos = hive.locate("wQ1")
        if white_queen_pos:
            if len(hive.level.occupied_surroundings(white_queen_pos)) > 5:
                res = -1 if inner_player == Player.WHITE else 1
        black_queen_pos = hive.locate("bQ1")
        if black_queen_pos:
            if len(hive.level.occupied_surroundings(black_queen_pos)) > 5:
                res = -1 if inner_player == Player.BLACK else 1
        return res

    @staticmethod
    def get_game_ended_original(board, player_num):
        hive = represent.load_state_with_player(board, AIEnvironment._player_to_inner_player(player_num))
        status = hive.check_victory()
        if status == GameStatus.UNFINISHED:
            return 0
        if player_num == 1:  # Hive.WHITE
            return -1 if status == GameStatus.BLACK_WIN else 1
        elif player_num == -1:  # Hive.BLACK
            return -1 if status == GameStatus.WHITE_WIN else 1
        else:
            raise ValueError('Unexpected game status')

    @staticmethod
    def get_valid_moves(board, player_num) -> List[int]:
        hive = represent.load_state_with_player(board, AIEnvironment._player_to_inner_player(player_num))
        return represent.get_all_action_vector(hive)

    @staticmethod
    def get_next_state(board, player_num, action_number):
        assert action_number >= 0
        hive = represent.load_state_with_player(board, AIEnvironment._player_to_inner_player(player_num))
        try:
            (piece, to_cell) = hive.action_from_vector(action_number)
        except engine.hive.HiveException as error:
            logging.error("HiveException was caught: {}".format(error))
            logging.error("action number: {}".format(action_number))
            utils.importexport.export_hive(hive, utils.importexport.saved_game_path("last_error.json"))
            raise
        # TODO handle pass
        try:
            hive.action_piece_to(piece, to_cell)
        except engine.hive.HiveException as error:
            logging.error("HiveException was caught: {}".format(error))
            logging.error("action number: {}, resulting action: ({}, {})".format(action_number, piece, to_cell))
            logging.error("Hive:\n{}".format(hive))
            utils.importexport.export_hive(hive, utils.importexport.saved_game_path("last_error.json"))
            raise
        return represent.two_dim_representation(represent.get_adjacency_state(hive)), player_num*(-1)

    
    @staticmethod
    def get_init_board():
        hive = engine.hive.Hive()
        return represent.two_dim_representation(represent.get_adjacency_state(hive))

    @staticmethod
    def get_symmetries(board: List[List[int]], pi):
        symmetries = []
        # Rotate the board 5 times
        for i in range(5):
            symmetries.append(AIEnvironment._rotate_adjacency(board))
        return [(sim, pi) for sim in symmetries]

    @staticmethod
    def _rotate_adjacency(two_dim_adjacency: List[List[int]]) -> List[List[int]]:
        result = []
        for row in two_dim_adjacency:
            new_row = []
            for direction in row:
                if 0 < direction <= 5:
                    new_row.append(direction + 1)
                elif direction == 6:
                    new_row.append(1)  # overflow of directions
                else:
                    new_row.append(direction)
            result.append(new_row)
        return result

    @staticmethod
    def get_board_size():
        hive = engine.hive.Hive()
        return represent.two_dim_representation(represent.canonical_adjacency_state(hive)).shape



ai_environment = AIEnvironment()
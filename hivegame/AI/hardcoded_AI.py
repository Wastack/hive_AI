from cmath import inf
import random
import logging

from engine.hive import Hive
from engine.environment.aienvironment import ai_environment
from engine.hive_utils import Player
import engine.hive_representation as representation


class MiniMaxAI():

    def __init__(self, hive: 'Hive', player_colour, default_depth):
        self.hive = hive
        self.player_colour = player_colour
        self.default_depth = default_depth

        self.piece_val_dict = {
            "Q": 50,
            "B": 20,
            "G": 20,
            "S": 10,
            "A": 30
        }

    def get_best_move(self):
        pass


    def minimax(self, position, depth, alpha, beta, maximizing_player):
        """
        Performs minimax algorithm recursively
        """
        if self.player_colour == Player.WHITE: player_num = 1
        else: player_num = -1
        actions_list = ai_environment.get_valid_moves(board, player_num)

        state = position
        board = ai_environment.get_init_board()


        if depth == 0 or ai_environment.get_game_ended(board) == 0:
            return self.get_static_evaluation(state, )

        if maximizing_player:
            max_eval = float('-inf')

            for i in range(len(actions_list)):
                if actions_list[i] == 1:
                    next_state = ai_environment.get_next_state(board, 1, i)
                    eval = self.minimax(next_state, depth - 1, alpha, beta, False)
                    max_eval = max(max_eval, eval)

                    alpha = max(alpha, eval)
                    if beta <= alpha:
                        break
            return max_eval

        else:
            min_eval = float('inf')

            for i in range(len(actions_list)):
                if actions_list[i] == 1:
                    next_state = ai_environment.get_next_state(board, 1, i)
                    eval = self.minimax(next_state, depth - 1, alpha, beta, True)
                    min_eval = min(min_eval, eval)

                    beta = min(beta, eval)
                    if beta <= alpha:
                        break
            return min_eval


        
    def get_static_evaluation(self, state, action, player_num):
        """"
        Function to run scores on current and next state and then compare scores
        """

        score = 0

        score += self.count_pinned_pieces_value(state)
        score += self.count_moveable_pieces_value(state)
        score += self.count_playable_space_value(state)
        score += self.count_moves_to_win_value(state)

        return score


    def count_pinned_pieces_value(self, state):
        """
        Given a state, this function returns the value of pinned pieces
        """
        return 0

    def count_moveable_pieces_value(self, state):
        """
        Function that gets a score representing the value of moveable pieces
        """
        return 0

    def count_playable_space_value(self, state):
        """
        Function to count the amount of space a new piece can be played in to for the opponent and for the current player
        """
        return 0

    def count_moves_to_win_value(self, state):
        """
        Function that counts the number of moves needed to win compared to the opponent
        """
        return 0

    def is_movement(self, action):
        """
        Function that gets the type of move (placement or movement). 
        Returns: False if the move is a placement and True if the move is a movement
        """
        return 0


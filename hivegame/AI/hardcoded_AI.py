from cmath import inf
import numpy as np

from engine.hive import Hive
from engine.environment.aienvironment import ai_environment
from engine.hive_utils import Player, get_queen_name
import engine.hive_representation as representation
import engine.hive_validation as validate

from typing import List


class MiniMaxAI():

    def __init__(self, hive: 'Hive', player_colour, depth):
        self.hive = hive
        self.depth = depth
        self.player_colour = player_colour

        self.piece_val_dict = {
            "Q": 50,
            "B": 20,
            "G": 20,
            "S": 10,
            "A": 30
        }

        # value of all pieces added up
        self.total_piece_value = 260

    def get_best_move(self):
        state = representation.two_dim_representation(representation.get_adjacency_state(self.hive))

        _, best_action_number = self.minimax(state, self.depth)
        best_action = self.hive.action_from_vector(best_action_number)

        return best_action


    def minimax(self, 
                position, 
                depth, 
                alpha = float('-inf'), 
                beta = float('inf'), 
                maximizing_player = True):
        """
        Performs minimax algorithm recursively

        Params:
            - position: of type List[List[int]], two dim representation of the board at a position
            - depth: of type int, how deep to search the tre
            - alpha: alpha value, used to recursively perform alpha-beta trimming, no need to pass new value
            - beta: beta value, used to recursively perform alpha-beta trimming, no need to pass new value
            - maximizing_player: used to recursively perform alpha-beta trimming, no need to pass new value

        Returns:
            - (min_eval, best_action) : min_eval is score of the action, which is used for recursion. best_action is
                the action number that had the best evaluation
        """

        # Some of these helper functions take a player_num instead of a colour. 
        # TODO refactor ai_environment functions to have consistent paramaters (take Player.colour instead of a number)
        if self.player_colour == Player.WHITE: 
            player_num = 1
            if maximizing_player:
                curr_player = Player.WHITE
            else:
                curr_player = Player.BLACK
        else: 
            player_num = -1
            if maximizing_player:
                curr_player = Player.BLACK
            else:
                curr_player = Player.WHITE

        # if the game has ended or we reach the end, then we get a score and return
        if depth == 0 or ai_environment.get_game_ended(position, player_num):
            return self.get_static_evaluation(position, curr_player), 0

        # perform recursion
        if maximizing_player:
            max_eval = float('-inf')
            actions_list = ai_environment.get_valid_moves(position, player_num)

            for i in range(len(actions_list)):
                if actions_list[i] == 1:
                    next_state, _ = ai_environment.get_next_state(position, player_num, i)
                    eval, _ = self.minimax(next_state, depth - 1, alpha, beta, False)

                    if max_eval < eval:
                        max_eval = eval
                        best_action = i

                    alpha = max(alpha, eval)
                    if beta <= alpha:
                        break
            return max_eval, best_action

        else:
            min_eval = float('inf')
            actions_list = ai_environment.get_valid_moves(position, -1*player_num)

            for i in range(len(actions_list)):
                if actions_list[i] == 1:
                    next_state, _ = ai_environment.get_next_state(position, -1*player_num, i)
                    eval, _ = self.minimax(next_state, depth - 1, alpha, beta, True)

                    if min_eval > eval:
                        min_eval = eval
                        best_action = i

                    beta = min(beta, eval)
                    if beta <= alpha:
                        break
            return min_eval, best_action


    def get_static_evaluation(self, board, curr_player):
        """"
        Function to run scores on current and next state and then compare scores
        
        Parameters:
            - state: 2D array representing the current board
            - player_num: 1 if our player is white and -1 if player is black
            - eval_opponent: Boolean if we want to evaluate our player or opponent player, default False

        Returns:
            - A score of the current position from the player_num's perspective
        """

        # loading state from corrent point of view

        game_state = representation.load_state_with_player(board, curr_player)
        score = 0

        score += 4* self.count_pinned_pieces_value_relative(game_state, curr_player)
        score += 4* self.count_moveable_pieces_value_relative(game_state, curr_player)
        score += 2* self.count_placeable_pieces_value(game_state, curr_player)
        score += 10* self.count_queen_surrounded_pieces(game_state, curr_player)

        # this value should dwarf the others and take absolute priority strategically
        score += 1000 * self.get_winning_score(board, curr_player)

        return score

    def count_pinned_pieces_value_relative(self, game_state, curr_player):
        """
        Given a state, this function returns the value of pinned pieces
        """
        if curr_player == Player.WHITE:     opp_player = Player.BLACK
        else:                               opp_player = Player.WHITE
        
        curr_val = self.get_pinned_piece_value(game_state, curr_player)
        opp_val = self.get_pinned_piece_value(game_state, opp_player)

        return curr_val - opp_val

        

    def get_pinned_piece_value(self, game_state, curr_player):
        pinned_piece_value = 0

        # pieces can only move once the queen has been placed
        queen_pos = game_state.locate(get_queen_name(curr_player))
        played_pieces = game_state.level.get_played_pieces(curr_player)

        if queen_pos:
            for piece in played_pieces:
                piece_pos = game_state.level.find_piece_position(piece)

                if not validate.validate_one_hive(game_state, piece_pos, piece):
                    # adding the value from value dict
                    val = self.piece_val_dict[piece.kind]
                    pinned_piece_value += val
        
        return pinned_piece_value / self.total_piece_value


    def count_moveable_pieces_value_relative(self, game_state, curr_player):
        """
        Function that gets a score representing the value of moveable pieces
        """

        if curr_player == Player.WHITE:     opp_player = Player.BLACK
        else:                               opp_player = Player.WHITE
        
        curr_val = self.get_moveable_piece_value(game_state, curr_player)
        opp_val = self.get_moveable_piece_value(game_state, opp_player)

        return curr_val - opp_val

    def get_moveable_piece_value(self, game_state, curr_player):
        moveable_piece_value = 0

        # pieces can only move once the queen has been placed
        queen_pos = game_state.locate(get_queen_name(curr_player))
        played_pieces = game_state.level.get_played_pieces(curr_player)

        if queen_pos:
            for piece in played_pieces:
                piece_pos = game_state.level.find_piece_position(piece)

                if not validate.validate_one_hive(game_state, piece_pos, piece):
                    continue
            
                val = self.piece_val_dict[piece.kind]
                moveable_piece_value += val
        
        return moveable_piece_value / self.total_piece_value

    def count_placeable_pieces_value(self, game_state, curr_player):
        """
        Function to count the amount of pieces that can be played
        """

        total_pieces = 11
        unplayed_pieces = game_state.level.get_unplayed_pieces(curr_player)

        # TODO reference dict for values instead of getting simple count
        if curr_player == Player.WHITE:
            opp_unplayed_pieces = game_state.level.get_unplayed_pieces(Player.BLACK)
        else:
            opp_unplayed_pieces = game_state.level.get_unplayed_pieces(Player.WHITE)

        return (len(unplayed_pieces) - len(opp_unplayed_pieces) ) / total_pieces


    def count_queen_surrounded_pieces(self, game_state, curr_player) -> (int):
        """
        Function that counts the number of pieces surrounding opponents queen bee versus current player's queen bee

        Returns:
            - an int in range {-1|1}
        """
        # since we are only querying the board statically, we can pass any colour player
        

        white_queen_pos = game_state.locate("wQ1")
        black_queen_pos = game_state.locate("bQ1")

        white_queen_surr = 0
        black_queen_surr = 0

        if white_queen_pos:
            white_queen_surr = len(game_state.level.occupied_surroundings(white_queen_pos)) / 6

        if black_queen_pos:
            black_queen_surr = len(game_state.level.occupied_surroundings(black_queen_pos)) / 6


        if curr_player == Player.WHITE:
            return black_queen_surr - white_queen_surr
        else:
            return white_queen_surr - black_queen_surr

    def get_winning_score(self, board, curr_player):
        """
        Gets the winning score for the current position
        Returns: int of value -1 if opponent won, 1 if player won and 0 if noone has won yet
        """

        if curr_player == Player.WHITE:     player_num = 1
        else:                               player_num = -1

        game_end = ai_environment.get_game_ended(board, player_num)
        return game_end



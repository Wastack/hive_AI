import logging
import math
from attr import validate
import numpy as np

from engine.hive_utils import Player
from engine.environment.aienvironment import ai_environment
from engine import hive_representation as represent

EPS = 1e-8

class MCTS():

    def __init__(self, model, args):
        self.model = model
        self.args = args
        self.Q_values = {}       
        self.visit_number_s_a = {}       # stores the visit number of an edge from state s with action a
        self.visit_number_s = {}        # stores the visit number of a state s
        self.policy_s = {}        # stores neural net policy at state s

        self.game_ended_s = {}        # records if game ended at a state s
        self.valid_moves_s = {}        # records valid moves at a state s

    def run(self, canonical_board, temperature=1):
        """
        Carries out numMCTSSims of Monte Carlo Tree Search

        Parameters:
            canonical_board: Canonical representation of the board.

        Returns:
            probabilities: the probability of each action as given by the monte carlo tree search
        """
        for i in range(self.args.numMCTSSims):
            #print("Monte Carlo Sim {}".format(i))
            self.search(canonical_board)

        state = ai_environment.string_representation(canonical_board)

        # Gathering results of counts of each visited edge in search tree
        counts = []
        for action in range(ai_environment.get_action_size()):
            if (state, action) in self.visit_number_s_a:
                counts.append(self.visit_number_s_a[(state, action)])
            else:
                counts.append(0)


        if temperature == 0:
            best_action = np.argmax(counts)
            probabilities = [0] * len(counts)
            probabilities[best_action] = 1
            return probabilities

        probabilities = []
        for i in range(len(counts)):
            counts[i] = counts[i]**(1./temperature)
            probabilities.append(counts[i]/float(sum(counts)))
        return probabilities

    def search(self, canonical_board):
        """
        Performs one iteration of Monte Carlo Tree Search

        Parameters:
            canonical_board: Canonical Representation of the board

        Returns:
            value: the negative of the value of the current canonical_board as given by MCTS
        """

        state = ai_environment.string_representation(canonical_board)

        # checking if we have reached a terminal node
        if state not in self.game_ended_s:
            self.game_ended_s[state] = ai_environment.get_game_ended(canonical_board, 1)
        if self.game_ended_s[state]!=0:
            return -self.game_ended_s[state]

        if state not in self.policy_s:
            # leaf node
            self.policy_s[state], value = self.model.predict(canonical_board)
            valids = ai_environment.get_valid_moves(canonical_board, 1)
            self.policy_s[state] = self.policy_s[state] * valids      # masking invalid moves
            sum_current_policy = np.sum(self.policy_s[state])

            # checking if we are masking all moves, if all moves are masked then NNET architecture may not be sufficient
            if sum_current_policy > 0:
                self.policy_s[state] /= sum_current_policy   
            else:
                print("All valid moves were masked, ignoring NNET output to select move")
                self.policy_s[state] = self.policy_s[state] + valids
                self.policy_s[state] /= np.sum(self.policy_s[state])

            self.valid_moves_s[state] = valids
            self.visit_number_s[state] = 0
            return -value

        action = self.get_best_ucb_action(state)


        # We very occasionally get an incorrect move, and I'm not entirely sure why.
        # These invalid moves all break the one hive rule, despite validating moves with ai_environment.get_valid_moves.
        # Instead of crashing the program in the middle of training we do a cheap workaround and take the first valid action instead.
        # These errors are so seldom that it will not negatively affect the training of the program.
        try:
            next_s, next_player = ai_environment.get_next_state(canonical_board, 1, action)
        except:
            logging.info("caught invalid move from MCTS")
            action = ai_environment.get_valid_moves(canonical_board, 1).index(1)
            next_s, next_player = ai_environment.get_next_state(canonical_board, 1, action)
        
        next_s = ai_environment.get_canonical_form(next_s, next_player)

        value = self.search(next_s)
        self.backpropogate(state, action, value)

        return -value

    def get_best_ucb_action(self, state):
        valids = self.valid_moves_s[state]
        currrent_best = -float('inf')
        best_action = -1

        # pick the action with the highest upper confidence bound (UCB) score
        for action in range(ai_environment.get_action_size()):
            if valids[action]:
                if (state, action) in self.Q_values:
                    # below is the UCB formula with Q values
                    ucb_score = self.Q_values[(state, action)] + self.args.cpuct * self.policy_s[state][action] * math.sqrt(
                            self.visit_number_s[state]) / (1 + self.visit_number_s_a[(state, action)])
                else:
                    # plain UCB formula without Q value approximation
                    ucb_score = self.args.cpuct * self.policy_s[state][action] * math.sqrt(self.visit_number_s[state] + EPS) 

                if ucb_score > currrent_best:
                    currrent_best = ucb_score
                    best_action = action

        return best_action


    def backpropogate(self, state, action, value):
        """"
        Function backpropogates value back up the tree by recording visit counts and Q value approximations

        Parameters:
            state: current state of the game at leaf node
            action: action to get to the current state
            value: value to backpropogate
        """

        if (state, action) in self.Q_values:
            total_value = self.visit_number_s_a[(state, action)] * self.Q_values[(state, action)] + value
            Q_val = total_value / (self.visit_number_s_a[(state, action)] + 1)
            self.Q_values[(state, action)] = Q_val
            self.visit_number_s_a[(state, action)] += 1

        else:
            self.Q_values[(state, action)] = value
            self.visit_number_s_a[(state, action)] = 1

        self.visit_number_s[state] += 1

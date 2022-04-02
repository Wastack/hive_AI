import logging
import math
import numpy as np

from engine.hive_utils import Player
from engine.environment.aienvironment import ai_environment
from engine import hive_representation as represent

EPS = 1e-8

class MCTS():

    def __init__(self, model, args):
        self.model = model
        self.args = args
        self.Q_values = {}       # stores Q values for s,a (as defined in the paper)
        self.visit_number_s_a = {}       # stores #times edge s,a was visited
        self.visit_number_s = {}        # stores #times board s was visited
        self.policy_s = {}        # stores initial policy (returned by neural net)

        self.game_ended_s = {}        # stores game.getGameEnded ended for board s
        self.valid_moves_s = {}        # stores game.getValidMoves for board s

    def run(self, canonical_board, temperature=1):
        """
        Carries out numMCTSSims of Monte Carlo Tree Search

        Parameters:
            canonical_board:  Canonical representation of the board.

        Returns:
            probs: a policy vector where the probability of the ith action is
                   proportional to visit_number_s_a[(s,a)]**(1./temp)
        """
        for i in range(self.args.numMCTSSims):
            #print("Monte Carlo Sim {}".format(i))
            self.search(canonical_board)

        state = ai_environment.string_representation(canonical_board)

        # Gathering results of counts of each visited edge in search tree
        for action in range(ai_environment.get_action_size):
            if (state, action) in self.visit_number_s_a:
                counts = self.visit_number_s_a[(state, action)]
            else:
                counts = 0

        if temperature == 0:
            bext_action = np.argmax(counts)
            probs = [0]*len(counts)
            probs[bext_action]=1
            return probs

        for count in counts:
            counts = [count**(1./temperature)]
            probs = [count/float(sum(counts))]
        return probs

    def search(self, canonical_board):
        """
        Performs one iteration of Monte Carlo Tree Search

        Parameters:
            canonical_board: Canonical Representation of the board

        Returns:
            v: the negative of the value of the current canonical_board
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
            if sum_current_policy > 0:
                self.policy_s[state] /= sum_current_policy    # re-normalize
            else:
                # if all valid moves were masked make all valid moves equally probable
                
                # NB! All valid moves may be masked if either your NNet architecture is insufficient or you've get overfitting or something else.
                # If you have got dozens or hundreds of these messages you should pay attention to your NNet and/or training process.
                print("All valid moves were masked, do workaround.")
                self.policy_s[state] = self.policy_s[state] + valids
                self.policy_s[state] /= np.sum(self.policy_s[state])

            self.valid_moves_s[state] = valids
            self.visit_number_s[state] = 0
            return -value

        valids = self.valid_moves_s[state]
        cur_best = -float('inf')
        best_act = -1

        # pick the action with the highest upper confidence bound
        for a in range(ai_environment.get_action_size()):
            if valids[a]:
                if (state, a) in self.Q_values:
                    u = self.Q_values[(state, a)] + self.args.cpuct * self.policy_s[state][a] * math.sqrt(
                            self.visit_number_s[state]) / (1 + self.visit_number_s_a[(state, a)])
                else:
                    u = self.args.cpuct * self.policy_s[state][a] * math.sqrt(self.visit_number_s[state] + EPS)     # Q = 0 ?

                if u > cur_best:
                    cur_best = u
                    best_act = a

        a = best_act
        next_s, next_player = ai_environment.get_next_state(canonical_board, 1, a)

        next_s = ai_environment.get_canonical_form(next_s, next_player)

        value = self.search(next_s)

        self.backpropogate(state, a, value)

        return -value


    def backpropogate(self, state, action, value):
        """"
        Function backpropogates value back up the tree

        Parameters:
            state: current state of the game at leaf node
            action: action to get to the current state
            value: value to backpropogate
        """

        if (state, action) in self.Q_values:
            self.Q_values[(state, action)] = (self.visit_number_s_a[(state, action)] * self.Q_values[(state, action)] + value) / (
                        self.visit_number_s_a[(state, action)] + 1)
            self.visit_number_s_a[(state, action)] += 1

        else:
            self.Q_values[(state, action)] = value
            self.visit_number_s_a[(state, action)] = 1

        self.visit_number_s[state] += 1

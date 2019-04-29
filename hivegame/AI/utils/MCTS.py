import math
import numpy as np
from hivegame.view import HiveView
from hivegame.hive_utils import HiveException
EPS = 1e-8

class MCTS():
    """
    Monte carlo tree search algorithm
    """

    def __init__(self, game, predictor, args):
        self.game = game
        self.predictor = predictor
        self.args = args
        self.Qsa = {}       # stores Q values for s,a (as defined in the paper)
        self.visit_number_s_a = {}       # stores #times edge s,a was visited
        self.visit_number_s = {}        # stores #times board s was visited
        self.policy_s = {}        # stores initial policy (returned by neural net)

        self.game_ended_s = {}        # stores game.getGameEnded ended for board s
        self.valid_moves_s = {}        # stores game.getValidMoves for board s

    def getActionProb(self, canonicalBoard, temp=1):
        """
        This function performs numMCTSSims simulations of MCTS starting from
        canonicalBoard.

        Returns:
            probs: a policy vector where the probability of the ith action is
                   proportional to Nsa[(s,a)]**(1./temp)
        """
        print("[DEBUG] getActionProb CALLED")
        for i in range(self.args.numMCTSSims):
            self.search(canonicalBoard)

        s = self.game.stringRepresentation(canonicalBoard)
        counts = [self.visit_number_s_a[(s, a)] if (s, a) in self.visit_number_s_a else 0 for a in range(self.game.getActionSize())]

        if temp==0:
            bestA = np.argmax(counts)
            probs = [0]*len(counts)
            probs[bestA]=1
            return probs

        counts = [x**(1./temp) for x in counts]
        probs = [x/float(sum(counts)) for x in counts]
        return probs

    def search(self, canonicalBoard):
        """
        This function performs one iteration of MCTS. It is recursively called
        till a leaf node is found. The action chosen at each node is one that
        has the maximum upper confidence bound as in the paper.

        Once a leaf node is found, the neural network is called to return an
        initial policy P and a value v for the state. This value is propagated
        up the search path. In case the leaf node is a terminal state, the
        outcome is propagated up the search path. The values of Ns, Nsa, Qsa are
        updated.

        NOTE: the return values are the negative of the value of the current
        state. This is done since v is in [-1,1] and if v is the value of a
        state for the current player, then its value is -v for the other player.

        Returns:
            v: the negative of the value of the current canonicalBoard
        """

        s = self.game.stringRepresentation(canonicalBoard)

        if s not in self.game_ended_s:
            self.game_ended_s[s] = self.game.getGameEnded(canonicalBoard, 1)
        if self.game_ended_s[s]!=0:
            # terminal node
            return -self.game_ended_s[s]

        if s not in self.policy_s:
            # leaf node
            self.policy_s[s], value = self.predictor.predict(canonicalBoard)
            valids = self.game.getValidMoves(canonicalBoard, 1)
            self.policy_s[s] = self.policy_s[s] * valids      # masking invalid moves
            sum_current_policy = np.sum(self.policy_s[s])
            if sum_current_policy > 0:
                self.policy_s[s] /= sum_current_policy    # re-normalize
            else:
                # if all valid moves were masked make all valid moves equally probable
                
                # NB! All valid moves may be masked if either your NNet architecture is insufficient or you've get overfitting or something else.
                # If you have got dozens or hundreds of these messages you should pay attention to your NNet and/or training process.
                print("All valid moves were masked, do workaround.")
                self.policy_s[s] = self.policy_s[s] + valids
                self.policy_s[s] /= np.sum(self.policy_s[s])

            self.valid_moves_s[s] = valids
            self.visit_number_s[s] = 0
            return -value

        valids = self.valid_moves_s[s]
        cur_best = -float('inf')
        best_act = -1

        # pick the action with the highest upper confidence bound
        for a in range(self.game.getActionSize()):
            if valids[a]:
                if (s,a) in self.Qsa:
                    u = self.Qsa[(s,a)] + self.args.cpuct * self.policy_s[s][a] * math.sqrt(self.visit_number_s[s]) / (1 + self.visit_number_s_a[(s, a)])
                else:
                    u = self.args.cpuct * self.policy_s[s][a] * math.sqrt(self.visit_number_s[s] + EPS)     # Q = 0 ?

                if u > cur_best:
                    cur_best = u
                    best_act = a

        a = best_act
        next_s, next_player = self.game.getNextState(canonicalBoard, 1, a)

        next_s = self.game.getCanonicalForm(next_s, next_player)

        value = self.search(next_s)

        if (s,a) in self.Qsa:
            self.Qsa[(s,a)] = (self.visit_number_s_a[(s, a)] * self.Qsa[(s, a)] + value) / (self.visit_number_s_a[(s, a)] + 1)
            self.visit_number_s_a[(s, a)] += 1

        else:
            self.Qsa[(s,a)] = value
            self.visit_number_s_a[(s, a)] = 1

        self.visit_number_s[s] += 1
        return -value

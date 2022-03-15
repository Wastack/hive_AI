import math
import numpy as np

from engine.environment.aienvironment import ai_environment

from engine import hive_representation

def ucb_score(parent, child, exploration_param = 1):
    """
    A method for calculating the Upper Confidence Bound (UCB)
    """
    priors = exploration_param * child.prior * math.sqrt(parent.visits_count) / (child.visits_count + 1)
    if child.visit_count > 0:
        # The child node is from the perspective of the opposing player, so signs must be reversed
        value = -child.value()
    else:
        value = 0

    return value + priors


class Node:
    """
    Defines a node in a monte carlo tree structure, class is defined with:
    - prior: prior probability of node
    - to_play: which player is currently able to play
    - visits_count: the number of visits this node has from a MCTS
    - children: the children nodes of this node
    - total_value: the total value accumulated through backpropogation
    - state: the state of the game in this node
    """
    def __init__(self, prior, to_play):
        self.prior = prior
        self.to_play = to_play
        self.visits_count = 0
        self.children = {}
        self.total_value = 0
        self.state = None

    def get_action(self, temperature):
        """
        Get the next action to be taken based on the visit count and the temperature
        """
        visits_counts = np.array([child.visits_count for child in self.children.values()])
        actions = [action for action in self.children.keys()]

        if temperature == float( 'inf' ):
            #if temp is infinity, we choose a random child
            next_action = np.random.choice(actions)
        elif temperature == 0:
            #if temp is 0 then we choose the most visited child node
            next_action = actions[np.argmax(visits_counts)]
        else:
            #calculating an array of probabilities for each action based on visits and temperature
            child_probabilities = visits_counts ** (1/temperature)
            child_probabilities = child_probabilities / sum(child_probabilities)
            next_action = np.random.choice(actions, p=child_probabilities)

        return next_action


    def select_best_child(self):
        """
        This method selects the child with the highest UCB score
        """
        best_score = float("-inf")
        best_action = -1
        best_child = None
        for action, child in self.children.items():
            score = ucb_score(self, child)
            if score > best_score:
                best_score = score
                best_action = action
                best_child = child
                
        return best_action, best_child


    def expand_node(self, state, to_play, action_probabilities):
        """
        Method to expand the children of a node while noting the priors given by the convolutional neural network
        """
        self.to_play - to_play
        self.state = state

        for action, probability in enumerate(action_probabilities):
            if probability != 0:
                self.children[action] = Node(prior=probability, to_play = self.to_play *-1)

    def value(self):
        """
        Return the value of the current node
        """
        if self.visits_count == 0:
            return 0
        else:
            return self.total_value / self.visits_count

    def is_expanded(self):
        """
        Return true if the node has been expanded and false if it hasn't
        """
        return len(self.children) > 0 

    def __repr__(self):
        return "{} Prior: {0:.3f} Count: {} Value: {}".format(self.state.__str__(), self.prior, self.visit_count, self.value)
    
    

class Monte_Carlo_Tree_Search():

    def __init__(self, game, model, args):
        #TODO complete init
        return

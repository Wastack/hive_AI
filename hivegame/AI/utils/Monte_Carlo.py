import math
import numpy as np

from engine.environment.aienvironment import ai_environment

from engine import hive_representation

def ucb_score(parent, child):
    #TODO implement ucb score calculation
    return

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
        

    def value(self):
        if self.visits_count == 0:
            return 0
        else:
            return self.total_value / self.visits_count

    def is_expanded(self):
        return len(self.children) > 0

    
    

class Monte_Carlo_Tree_Search():

    def __init__(self, game, model, args):
        #TODO complete init
        return

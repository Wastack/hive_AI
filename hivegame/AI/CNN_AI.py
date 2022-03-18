from engine.environment.aienvironment import AIEnvironment
from AI.random_player import RandomPlayer
from arena import Arena
from engine.hive_utils import dotdict
from project import ROOT_DIR

import numpy as np

from keras.models import *
from keras.layers import *
from keras.optimizers import *

class CNNModel(nn.Module):
    def _init_(self, board_size, action_size, device):
        
        super(CNNModel, self).__init__()

        self.device = device
        self.board_size = board_size
        self.action_size = action_size



import logging
import sys

from hivegame.AI.utils.keras.NNet import NNetWrapper
from hivegame.AI.utils.Coach import Coach
from hivegame.environment import Environment
from hive_utils import *


args = dotdict({
    'numIters': 1000,
    'numEps': 100,
    'tempThreshold': 15,
    'updateThreshold': 0.6,
    'maxlenOfQueue': 200000,
    'numMCTSSims': 25,
    'arenaCompare': 40,
    'cpuct': 1,

    'checkpoint': './temp/',
    'load_model': False,
    'load_folder_file': ('/dev/models/8x100x50','best.pth.tar'),
    'numItersForTrainExamplesHistory': 20,

})

def main():
    logging.basicConfig(level=logging.INFO)
    env = Environment()
    nnet = NNetWrapper(env)
    c = Coach(env, nnet, args)
    c.learn()

if __name__ == '__main__':
    sys.exit(main())
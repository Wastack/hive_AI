import logging
import sys

from hivegame.AI.utils.keras.NNet import NNetWrapper
from hivegame.AI.utils.Coach import Coach
from hivegame.AI.environment import Environment
from hivegame.hive_utils import *


args = dotdict({
    'numIters': 3,
    'numEps': 5,
    'tempThreshold': 15,
    'updateThreshold': 0.5,
    'maxlenOfQueue': 200000,
    'numMCTSSims': 2,
    'arenaCompare': 40,
    'cpuct': 0.1,

    'checkpoint': './temp/',
    'load_model': False,
    'load_folder_file': ('/dev/models/8x100x50','best.pth.tar'),
    'numItersForTrainExamplesHistory': 20,

})

def main():
    FORMAT = "[%(filename)s:%(lineno)s - %(funcName)20s() ] %(message)s"
    logging.basicConfig(level=logging.DEBUG, format=FORMAT)
    env = Environment()
    nnet = NNetWrapper(env)
    c = Coach(env, nnet, args)
    c.learn()

if __name__ == '__main__':
    sys.exit(main())
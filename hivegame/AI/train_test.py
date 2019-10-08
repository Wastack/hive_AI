import logging
import sys, os

from hivegame.AI.utils.keras.NNet import NNetWrapper
from hivegame.AI.utils.Coach import Coach
from hivegame.AI.environment import Environment
from hivegame.hive_utils import *


args = dotdict({
    'numIters': 10,
    'numEps': 7,
    'tempThreshold': 15,
    'updateThreshold': 0.5,
    'maxlenOfQueue': 200000,
    'numMCTSSims': 2,
    'arenaCompare': 40,
    'cpuct': 0.8,

    'checkpoint': './temp/',
    'load_model': False,
    'load_folder_file': ('/dev/models/8x100x50','best.pth.tar'),
    'numItersForTrainExamplesHistory': 20,

})

def main():
    sys.setrecursionlimit(1500)
    FORMAT = "[%(filename)s:%(lineno)s - %(funcName)20s() ] %(message)s"
    logging.basicConfig(level=logging.DEBUG, format=FORMAT)
    env = Environment()
    nnet = NNetWrapper(env)
    c = Coach(env, nnet, args)
    c.learn()

    # save model
    from project import ROOT_DIR
    nnet.save_model(os.path.join(ROOT_DIR, 'model_saved'), "model.h5")

if __name__ == '__main__':
    sys.exit(main())
import sys, os

import logging

from AI.alpha_player import AlphaPlayer
from AI.environment import Environment
from AI.random_player import RandomPlayer
from AI.utils.keras.NNet import NNetWrapper
from arena import Arena
from hive_utils import dotdict
from project import ROOT_DIR

args = dotdict({
    'numIters': 28,
    'numEps': 7,
    'tempThreshold': 15,
    'updateThreshold': 0.5,
    'maxlenOfQueue': 200000,
    'numMCTSSims': 2,
    'arenaCompare': 40,
    'cpuct': 0.3,

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
    nnet.load_model(folder=os.path.join(ROOT_DIR, 'model_saved'), filename='model.h5')
    alphaPlayer = AlphaPlayer(env, nnet, args)
    randomPlayer = RandomPlayer()
    arena = Arena(alphaPlayer, randomPlayer, env)
    alpha_wins, random_wins, draws = arena.playGames(5000)
    print("aplha won: {} times, random won: {} times, number of draws: {}".format(alpha_wins, random_wins, draws))


if __name__ == '__main__':
    sys.exit(main())
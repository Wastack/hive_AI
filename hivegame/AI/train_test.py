import logging
import sys, os

from configure import train_args
from AI.utils.keras.NNet import NNetWrapper
from AI.utils.Coach import Coach


def main():
    sys.setrecursionlimit(1500)
    FORMAT = "[%(filename)s:%(lineno)s - %(funcName)20s() ] %(message)s"
    logging.basicConfig(level=logging.DEBUG, format=FORMAT)

    nnet = NNetWrapper()
    c = Coach(nnet, train_args)
    c.learn()
    # save model
    from project import ROOT_DIR
    nnet.save_model(os.path.join(ROOT_DIR, 'model_saved'), "model.h5")


if __name__ == '__main__':
    sys.exit(main())
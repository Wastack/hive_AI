import logging
import sys, os

from configure import train_args, nnet_args
from AI.CNN_AI import CNNModel
from AI.trainer import Trainer


def main():

    sys.setrecursionlimit(3000)
    FORMAT = "[%(filename)s:%(lineno)s - %(funcName)20s() ] %(message)s"
    logging.basicConfig(level=logging.DEBUG, format=FORMAT)

    nnet = CNNModel(nnet_args)
    trainer = Trainer(nnet, train_args, nnet_args)
    trainer.learn()
    # save model
    from project import ROOT_DIR
    nnet.save_model(os.path.join(ROOT_DIR, 'model_saved'), "model.h5")


if __name__ == '__main__':
    sys.exit(main())
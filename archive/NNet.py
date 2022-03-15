import os
import time
import numpy as np
import sys

import logging

sys.path.append('../..')
from engine.hive_utils import dotdict
from archive.NeuralNet import NeuralNet
from hivegame.engine.environment.aienvironment import ai_environment

from .HiveNNet import HiveNNet as hivenet
from keras.models import load_model

args = dotdict({
    'lr': 0.001,
    'dropout': 0.3,
    'epochs': 10,
    'batch_size': 64,
    'cuda': False,
    'num_channels': 16,
})

class NNetWrapper(NeuralNet):
    def __init__(self):
        self.nnet = hivenet(args)
        self.board_x, self.board_y = ai_environment.getBoardSize()
        self.action_size = ai_environment.getActionSize()

    def train(self, examples):
        """
        examples: list of examples, each example is of form (board, pi, v)
        """
        input_boards, target_pis, target_vs = list(zip(*examples))
        input_boards = np.asarray(input_boards)
        logging.debug("input dimensions: {}".format(input_boards.shape))
        target_pis = np.asarray(target_pis)
        target_vs = np.asarray(target_vs)
        self.nnet.model.fit(x = input_boards, y = [target_pis, target_vs], batch_size = args.batch_size, epochs = args.epochs)

    def predict(self, board):
        """
        board: np array with board
        """
        # timing
        start = time.time()

        # preparing input
        board = np.array(board[np.newaxis, :, :], dtype=np.float64)

        # run
        pi, v = self.nnet.model.predict(board)

        #print('PREDICTION TIME TAKEN : {0:03f}'.format(time.time()-start))
        return pi[0], v[0]

    def save_checkpoint(self, folder='checkpoint', filename='checkpoint.pth.tar'):
        filepath = os.path.join(folder, filename)
        if not os.path.exists(folder):
            print("Checkpoint Directory does not exist! Making directory {}".format(folder))
            os.mkdir(folder)
        else:
            print("Checkpoint Directory exists! ")
        self.nnet.model.save_weights(filepath)

    def load_checkpoint(self, folder='checkpoint', filename='checkpoint.pth.tar'):
        # https://github.com/pytorch/examples/blob/master/imagenet/main.py#L98
        filepath = os.path.join(folder, filename)
        if not os.path.exists(filepath):
            raise(RuntimeError("No model in path {}".format(filepath)))
        self.nnet.model.load_weights(filepath)

    def save_model(self, folder='checkpoint', filename='model.h5'):
        file_path = os.path.join(folder, filename)
        if not os.path.exists(folder):
            os.mkdir(folder)
        self.nnet.model.save(file_path)

    def load_model(self, folder='checkpoint', filename='model.h5'):
        file_path = os.path.join(folder, filename)
        if not os.path.exists(file_path):
            raise(RuntimeError("No model in path {}".format(file_path)))
        self.nnet.model = load_model(file_path)

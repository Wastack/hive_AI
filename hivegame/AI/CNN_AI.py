from engine.environment.aienvironment import ai_environment
from engine.hive_utils import dotdict

import numpy as np
import time
import os

from keras.models import Model, load_model
from keras.layers import *
from keras.optimizers import adam_v2



class CNNModel():
    def __init__(self, nnet_args):

        # game params
        self.board_x, self.board_y = ai_environment.get_board_size()
        self.action_size = ai_environment.get_action_size()
        self.args = nnet_args
        print("[INFO] Create nnet with: board_x: {}, board_y: {}, action_size: {}, args: {} ".format(self.board_x,
                                                                                                    self.board_y,
                                                                                                    self.action_size,
                                                                                                    self.args))

        # Neural Net
        self.input_boards = Input(shape=(self.board_x, self.board_y))    # s: batch_size x board_x x board_y

        x_image = Reshape((self.board_x, self.board_y, 1))(self.input_boards)                # batch_size  x board_x x board_y x 1
        h_conv1 = Activation('relu')(BatchNormalization(axis=3)(Conv2D(self.args.num_channels, 3, padding='same', use_bias=False)(x_image)))         # batch_size  x board_x x board_y x num_channels
        h_conv2 = Activation('relu')(BatchNormalization(axis=3)(Conv2D(self.args.num_channels, 3, padding='same', use_bias=False)(h_conv1)))         # batch_size  x board_x x board_y x num_channels
        h_conv3 = Activation('relu')(BatchNormalization(axis=3)(Conv2D(self.args.num_channels, 3, padding='valid', use_bias=False)(h_conv2)))        # batch_size  x (board_x-2) x (board_y-2) x num_channels
        h_conv4 = Activation('relu')(BatchNormalization(axis=3)(Conv2D(self.args.num_channels, 3, padding='valid', use_bias=False)(h_conv3)))        # batch_size  x (board_x-4) x (board_y-4) x num_channels
        h_conv4_flat = Flatten()(h_conv4)
        s_fc1 = Dropout(self.args.dropout)(Activation('relu')(BatchNormalization(axis=1)(Dense(1024, use_bias=False)(h_conv4_flat))))  # batch_size x 1024
        s_fc2 = Dropout(self.args.dropout)(Activation('relu')(BatchNormalization(axis=1)(Dense(512, use_bias=False)(s_fc1))))          # batch_size x 1024
        self.pi = Dense(self.action_size, activation='softmax', name='pi')(s_fc2)   # batch_size x self.action_size
        self.v = Dense(1, activation='tanh', name='v')(s_fc2)                    # batch_size x 1

        self.model = Model(inputs=self.input_boards, outputs=[self.pi, self.v])
        opt = adam_v2.Adam(learning_rate=self.args.lr)
        self.model.compile(loss=['categorical_crossentropy','mean_squared_error'], optimizer=opt)

    def train(self, examples):
        """
        examples: list of examples, each example is of form (board, pi, v)
        """
        print(np.shape(examples))
        print(np.shape(list(zip(*examples))))
        print(np.shape(list(zip(zip(*examples)))))
        input_boards, target_pis, target_vs = list(zip(*examples))
        input_boards = np.asarray(input_boards)
        target_pis = np.asarray(target_pis)
        target_vs = np.asarray(target_vs)
        self.model.fit(x = input_boards, y = [target_pis, target_vs], batch_size = self.args.batch_size, epochs = self.args.epochs)

    def predict(self, board):
        """
        board: np array with board
        """
        # timing
        start = time.time()

        # preparing input
        board = np.array(board[np.newaxis, :, :], dtype=np.float64)

        # run
        pi, v = self.model.predict(board)

        print('PREDICTION TIME TAKEN : {0:03f}'.format(time.time()-start))
        return pi[0], v[0]

    def save_model(self, folder='checkpoint', filename='model.h5'):
        file_path = os.path.join(folder, filename)
        if not os.path.exists(folder):
            os.mkdir(folder)
        self.model.save(file_path)

    def load_model(self, folder='checkpoint', filename='model.h5'):
        file_path = os.path.join(folder, filename)
        if not os.path.exists(file_path):
            raise(RuntimeError("No model in path {}".format(file_path)))
        self.model = load_model(file_path)

    def save_checkpoint(self, folder='checkpoint', filename='checkpoint.h5'):
        filepath = os.path.join(folder, filename)
        if not os.path.exists(folder):
            print("Checkpoint Directory does not exist! Making directory {}".format(folder))
            os.mkdir(folder)
        else:
            print("Checkpoint Directory exists! ")
        self.model.save_weights(filepath)

    def load_checkpoint(self, folder='checkpoint', filename='checkpoint.h5'):
        filepath = os.path.join(folder, filename)
        if not os.path.exists(filepath):
            raise(RuntimeError("No model in path {}".format(filepath)))
        self.model.load_weights(filepath)




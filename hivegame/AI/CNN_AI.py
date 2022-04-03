from engine.environment.aienvironment import ai_environment
from engine.hive_utils import dotdict

import numpy as np
import os

from keras.models import Model, load_model
from keras.layers import *
from keras.optimizers import adam_v2



class CNNModel():
    def __init__(self, nnet_args):

        # getting the game parameters for the NNET
        self.board_x, self.board_y = ai_environment.get_board_size()
        self.action_size = ai_environment.get_action_size()
        self.args = nnet_args
        print("Creating neural network with: board_x: {}, board_y: {}, action_size: {}, args: {} ".format(self.board_x,
                                                                                                    self.board_y,
                                                                                                    self.action_size,
                                                                                                    self.args))

        # Neural Net
        self.input_boards = Input(shape=(self.board_x, self.board_y))

        x_image = Reshape((self.board_x, self.board_y, 1))(self.input_boards)

        # applying series of 2D convolutional layers with relu activation to learn board representation
        # conv window should be 3 to get adjacent pieces from each piece
        y = Conv2D(self.args.num_channels, 3, padding='same', use_bias=False)(x_image)
        y = BatchNormalization(axis=3)(y)
        y = Activation('relu')(y)

        y = Conv2D(self.args.num_channels, 3, padding='same', use_bias=False)(x_image)
        y = BatchNormalization(axis=3)(y)
        y = Activation('relu')(y)

        y = Conv2D(self.args.num_channels, 3, padding='valid', use_bias=False)(x_image)
        y = BatchNormalization(axis=3)(y)
        y = Activation('relu')(y)

        y = Conv2D(self.args.num_channels, 3, padding='valid', use_bias=False)(x_image)
        y = BatchNormalization(axis=3)(y)
        y = Activation('relu')(y)

        y = Flatten()(y)

        # applying a series of dense layers with dropout to learn representations of action space
        y = Dense(2048, use_bias=False)(y)
        y = BatchNormalization(axis=1)(y)
        y = Dropout(self.args.dropout)(y)

        y = Dense(1024, use_bias=False)(y)
        y = BatchNormalization(axis=1)(y)
        y = Dropout(self.args.dropout)(y)

        y = Dense(512, use_bias=False)(y)
        y = BatchNormalization(axis=1)(y)
        y = Dropout(self.args.dropout)(y)


        self.policy = Dense(self.action_size, activation='softmax', name='policy')(y) 
        self.v = Dense(1, activation='tanh', name='v')(y)

        self.model = Model(inputs=self.input_boards, outputs=[self.policy, self.v])
        opt = adam_v2.Adam(learning_rate=self.args.lr)
        self.model.compile(loss=['categorical_crossentropy','mean_squared_error'], optimizer=opt)

    def train(self, examples):
        input_boards, target_policys, target_vs = list(zip(*examples))
        input_boards = np.asarray(input_boards)
        target_policys = np.asarray(target_policys)
        target_vs = np.asarray(target_vs)
        self.model.fit(x = input_boards, y = [target_policys, target_vs], batch_size = self.args.batch_size, epochs = self.args.epochs)

    def predict(self, board):
        board = np.array(board[np.newaxis, :, :], dtype=np.float64)
        policy, v = self.model.predict(board)

        return policy[0], v[0]

    def save_model(self, folder='checkpoint', filename='model.h5'):
        file_path = os.path.join(folder, filename)
        if not os.path.exists(folder):
            os.mkdir(folder)
        self.model.save(file_path)
        print("Saving model to: {}/{}".format(folder, filename))

    def load_model(self, folder='checkpoint', filename='model.h5'):
        file_path = os.path.join(folder, filename)
        if not os.path.exists(file_path):
            raise(RuntimeError("Could not find file_path {}".format(file_path)))
        self.model = load_model(file_path)

    def save_checkpoint(self, folder='checkpoint', filename='checkpoint.h5'):
        filepath = os.path.join(folder, filename)
        if not os.path.exists(folder):
            os.mkdir(folder)
        self.model.save_weights(filepath)

    def load_checkpoint(self, folder='checkpoint', filename='checkpoint.h5'):
        filepath = os.path.join(folder, filename)
        if not os.path.exists(filepath):
            raise(RuntimeError("Could not find file_path {}".format(filepath)))
        self.model.load_weights(filepath)




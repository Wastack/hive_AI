import sys

from hivegame.engine.environment.aienvironment import ai_environment
from contextlib import redirect_stderr
import os

sys.path.append('..')

withGPU = False
with redirect_stderr(open(os.devnull, "w")):
    if withGPU:
        from tensorflow.keras.models import *
        from tensorflow.keras.layers import *
        from tensorflow.keras.optimizers import *
        import tensorflow as tf
    else:
        from keras.models import *
        from keras.layers import *
        from keras.optimizers import *


class HiveNNet():
    def __init__(self, args):

        if withGPU:
            gpus = tf.config.experimental.list_physical_devices('GPU')
            if gpus:
                try:
                    for gpu in gpus:
                        tf.config.experimental.set_memory_growth(gpu, True)

                except RuntimeError as e:
                    print(e)


        # game params
        self.board_x, self.board_y = ai_environment.getBoardSize()
        self.action_size = ai_environment.getActionSize()
        self.args = args
        print("[INFO] Create nnet with: board_x: {}, board_y: {}, action_size: {}, args: {} ".format(self.board_x,
                                                                                                    self.board_y,
                                                                                                    self.action_size,
                                                                                                    args))

        # Neural Net
        self.input_boards = Input(shape=(self.board_x, self.board_y))    # s: batch_size x board_x x board_y

        x_image = Reshape((self.board_x, self.board_y, 1))(self.input_boards)                # batch_size  x board_x x board_y x 1
        h_conv1 = Activation('relu')(BatchNormalization(axis=3)(Conv2D(args.num_channels, 3, padding='same', use_bias=False)(x_image)))         # batch_size  x board_x x board_y x num_channels
        h_conv2 = Activation('relu')(BatchNormalization(axis=3)(Conv2D(args.num_channels, 3, padding='same', use_bias=False)(h_conv1)))         # batch_size  x board_x x board_y x num_channels
        h_conv3 = Activation('relu')(BatchNormalization(axis=3)(Conv2D(args.num_channels, 3, padding='valid', use_bias=False)(h_conv2)))        # batch_size  x (board_x-2) x (board_y-2) x num_channels
        h_conv4 = Activation('relu')(BatchNormalization(axis=3)(Conv2D(args.num_channels, 3, padding='valid', use_bias=False)(h_conv3)))        # batch_size  x (board_x-4) x (board_y-4) x num_channels
        h_conv4_flat = Flatten()(h_conv4)
        s_fc1 = Dropout(args.dropout)(Activation('relu')(BatchNormalization(axis=1)(Dense(1024, use_bias=False)(h_conv4_flat))))  # batch_size x 1024
        s_fc2 = Dropout(args.dropout)(Activation('relu')(BatchNormalization(axis=1)(Dense(512, use_bias=False)(s_fc1))))          # batch_size x 1024
        self.pi = Dense(self.action_size, activation='softmax', name='pi')(s_fc2)   # batch_size x self.action_size
        self.v = Dense(1, activation='tanh', name='v')(s_fc2)                    # batch_size x 1

        self.model = Model(inputs=self.input_boards, outputs=[self.pi, self.v])
        self.model.compile(loss=['categorical_crossentropy','mean_squared_error'], optimizer=Adam(args.lr))

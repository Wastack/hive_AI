from engine.hive_utils import dotdict

# arguments for training the NNet AI in train_test.py
train_args = dotdict({
    'numIters': 15,
    'numEps': 10,
    'tempThreshold': 15,
    'updateThreshold': 0.5,
    'maxlenOfQueue': 500000,
    'numMCTSSims': 20,
    'arenaCompare': 40,
    'cpuct': 0.8,
    'maxMCTSRuns': 100,

    'checkpoint': './temp/',
    'load_model': False,
    'load_folder_file': ('/dev/models/8x100x50','best.pth.tar'),
    'numItersForTrainExamplesHistory': 300,

})

# arguments for the neural network model
nnet_args = dotdict({
    'lr': 0.001,
    'dropout': 0.2,
    'epochs': 10,
    'batch_size': 64,
    'num_channels': 16,
})

# arguments for the minimax evaluation
minimax_args = dotdict({
    'pinned_value': 4.,
    'moveable_piece_value': 2.,
    'placeable_piece_value': 1.,
    'number_moves_value': 2.,
    'queen_surrounded_value': 8.,
    'winning_value': 1000.
})

# variable for the number of pieces surrounding opponents queen to win
surrounded_to_win = 3
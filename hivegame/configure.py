from engine.hive_utils import dotdict

# arguments for training the NNet AI in train_test.py
train_args = dotdict({
    'numIters': 10,
    'numEps': 8,
    'tempThreshold': 15,
    'updateThreshold': 0.5,
    'maxlenOfQueue': 500000,
    'numMCTSSims': 80,
    'arenaCompare': 40,
    'cpuct': 0.8,

    'checkpoint': './temp/',
    'load_model': False,
    'load_folder_file': ('/dev/models/8x100x50','best.pth.tar'),
    'numItersForTrainExamplesHistory': 100,

})

# arguments for the neural network model
nnet_args = dotdict({
    'lr': 0.001,
    'dropout': 0.3,
    'epochs': 10,
    'batch_size': 64,
    'cuda': False,
    'num_channels': 16,
})

# arguments for the minimax evaluation
minimax_args = dotdict({
    'pinned_value': 12,
    'moveable_piece_value': 4,
    'placeable_piece_value': 1,
    'number_moves_value': 16,
    'queen_surrounded_value': 200,
    'winning_value': 1000
})
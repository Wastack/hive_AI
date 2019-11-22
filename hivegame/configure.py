from hivegame.engine.hive_utils import dotdict

train_args = dotdict({
    'numIters': 10,
    'numEps': 7,
    'tempThreshold': 15,
    'updateThreshold': 0.5,
    'maxlenOfQueue': 200000,
    'numMCTSSims': 5,
    'arenaCompare': 40,
    'cpuct': 0.8,

    'checkpoint': './temp/',
    'load_model': False,
    'load_folder_file': ('/dev/models/8x100x50','best.pth.tar'),
    'numItersForTrainExamplesHistory': 20,

})
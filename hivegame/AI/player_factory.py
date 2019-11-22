import os
import sys
from typing import Tuple, List

from hivegame.AI.alpha_player import AlphaPlayer
from hivegame.AI.human_player import HumanPlayer
from hivegame.AI.player import Player
from hivegame.AI.random_player import RandomPlayer
from hivegame.AI.utils.keras.NNet import NNetWrapper
from hivegame.engine.hive_utils import dotdict
from hivegame.project import ROOT_DIR
import logging


# TODO make this configurable
mcts_dotdict = dotdict({
    "numMCTSSims" : 5,
    "cpuct" : 1
})

def create_alpha(arg_opts):
    model_path = arg_opts.model_path
    if model_path:
        file = os.path.basename(model_path)
        folder = os.path.dirname(model_path)
    else:
        folder = os.path.join(ROOT_DIR, 'model_saved')
        file = 'model.h5'

    nnet = NNetWrapper()
    nnet.load_model(folder=os.path.join(ROOT_DIR, 'model_saved'), filename='model.h5')
    logging.info("Load neural network file: {} from folder: {}".format(file, folder))
    return AlphaPlayer(nnet, mcts_dotdict)

def create_random(arg_opts):
    return RandomPlayer()

def create_human(arg_opts):
    return HumanPlayer(sys.stdin)


players = {
    "alpha_player" : create_alpha,
    "random_player" : create_random,
    "human_ascii" : create_human,
    "human_gui" : lambda _: _
}


def registered_players() -> List[str]:
    return list(players.keys())


def create_players(arg_opts) -> Tuple[Player, Player]:
    player1 = players[arg_opts.player_white](arg_opts)
    player2 = players[arg_opts.player_black](arg_opts)

    return (player1, player2)
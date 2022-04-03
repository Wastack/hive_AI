import argparse
import logging
import os
import sys

from AI.player_factory import create_players, registered_players
from AI.trainer import Trainer
from AI.CNN_AI import CNNModel
from arena import Arena
from hivegame.configure import train_args


def main():
    FORMAT = "[%(filename)s:%(lineno)s - %(funcName)20s() ] %(message)s"
    logging.basicConfig(level=logging.DEBUG, format=FORMAT)
    parser = argparse.ArgumentParser(description="Platform for playing Hive and training AI's for Hive")
    parser.add_argument('--with-player-white', help='Specify agent to use white player. Possible values: {}'
                        .format(registered_players()),
                        dest="player_white", default="human_ascii", action="store")
    parser.add_argument('--with-player-black', help='Specify agent to use as black player.'
                                                    'See possible values at option --with-player-white',
                        dest="player_black", default="human_ascii", action="store")
    parser.add_argument('--disable-gui', help='Disable Graphical User Interface. With this option set,'
                                              'the project has no dependency on Qt5',
                        dest='gui_enabled', const=False, default=True, action="store_const")
    parser.add_argument('--train-aplha-ai', help='Train Alpha Player with the parameters given in configure.py',
                        const=True, default=False, dest="train_alpha", action="store_const")
    parser.add_argument('--game-number', help="Define number of games to play.", default=1, dest="game_number",
                        action="store")
    opt_args = parser.parse_args()

    if opt_args.train_alpha:
        sys.setrecursionlimit(1500)
        nnet = CNNModel()
        c = Trainer(nnet, train_args)
        c.learn()

        # save model
        from project import ROOT_DIR
        nnet.save_model(os.path.join(ROOT_DIR, 'model_saved'), "model.h5")
        return

    player1, player2 = create_players(opt_args)

    logging.info(f"GUI enabled: {opt_args.gui_enabled}")
    logging.info(f"Number of games to play: {opt_args.game_number}")
    logging.info(f"Player 1: {opt_args.player_white}")
    logging.info(f"Player 2: {opt_args.player_black}")
    game = Arena(player1, player2)        
    game.playGames(opt_args.game_number)

    logging.info("Thanks for playing Hive. Have a nice day!")


if __name__ == '__main__':
    sys.exit(main())
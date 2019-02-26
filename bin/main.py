#! /usr/bin/env python

import time
import sys
from hivegame.board import HexBoard
from hivegame.hive import Hive, HiveException
from hivegame.piece import HivePiece
from hivegame.view import HiveView
from hivegame.environment import Environment


class HiveShellClient(object):
    """HiveShellClient is a command line client to the Hive game."""

    def __init__(self):
        super(HiveShellClient, self).__init__()
        self.input = sys.stdin
        self.env = Environment()

    def run(self):
        self.env.reset_game()
        self.view = HiveView(self.env.hive)


        while self.env.check_victory() == Hive.UNFINISHED:
            print("Turn: %s" % self.env.get_turn_count())
            active_player = self.env.current_player()
            print(self.view)
            print("pieces available: %s" % sorted(
                self.env.unplayed_pieces(active_player).keys()
            ))
            print("player %s play: " % active_player)
            try:
                cmd = self.input.readline()
            except KeyboardInterrupt:
                break
            if self.env.exec_cmd(cmd.strip()):
                print()
                print("=" * 79)
                print()
            else:
                print("invalid play!")

        print("\nThanks for playing Hive. Have a nice day!")


def main():

    game = HiveShellClient()
    game.run()


if __name__ == '__main__':
    sys.exit(main())

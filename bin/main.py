#! /usr/bin/env python

import time
import sys
from hivegame.board import HexBoard
from hivegame.hive import Hive, HiveException
from hivegame.view import HiveView
from hivegame.environment import Environment
from hivegame.AI.random_ai import RandomAI


class HiveShellClient(object):
    """HiveShellClient is a command line client to the Hive game."""

    def __init__(self):
        super(HiveShellClient, self).__init__()
        self.input = sys.stdin
        self.env = Environment()

    def run(self):
        self.env.reset_game()
        self.view = HiveView(self.env.hive)
        ai1 = RandomAI()


        while self.env.check_victory() == Hive.UNFINISHED:
            if self.env.current_player() == "b":
                response = ai1.step(self.env)
                if not response:
                    self.env.exec_cmd("pass")
                    print("DEBUG: AI passed")
                    continue
                (piece, coord) = response
                print("DEBUG: choosen action is: ({}, {})".format(piece,coord) )
                self.env.hive.action_piece_to(piece, coord)
            else:
                if not self.human_turn():
                    break

        print("\nThanks for playing Hive. Have a nice day!")

    def human_turn(self):
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
            return False
        if self.env.exec_cmd(cmd.strip()):
            print()
            print("=" * 79)
            print()
        else:
            print("invalid play!")
        return True
    

def main():

    game = HiveShellClient()
    game.run()


if __name__ == '__main__':
    sys.exit(main())

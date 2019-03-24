#! /usr/bin/env python

import sys
from hivegame.hive import Hive
from hivegame.environment import Environment
from hivegame.AI.random_ai import RandomAI
from hivegame.AI.human_ai import HumanAI

import logging


class Arena(object):

    def __init__(self, player1, player2):
        super(Arena, self).__init__()
        self.env = Environment()
        self._player1 = player1
        self._player2 = player2

    def run(self):
        self.env.reset_game()

        while self.env.check_victory() == Hive.UNFINISHED:
            current_player = self._player1 if self.env.current_player() == "w" else self._player2
            response = current_player.step(self.env)
            if response == "pass":
                self.env.exec_cmd("pass")
                continue
            # TODO refactor human AI to look the same from outside
            if isinstance(current_player, HumanAI):
                if not response:
                    break
                feedback = self.env.exec_cmd(response)
            else:
                (piece, coord) = response
                feedback = self.env.action_piece_to(piece, coord)
            current_player.feedback(feedback)

        print("\nThanks for playing Hive. Have a nice day!")


def main():
    logging.basicConfig(level=logging.INFO)
    # game = Arena(HumanAI(sys.stdin), RandomAI())
    game = Arena(RandomAI(), RandomAI())
    game.run()


if __name__ == '__main__':
    sys.exit(main())

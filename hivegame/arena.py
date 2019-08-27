#! /usr/bin/env python

import sys
from AI.environment import Environment
from hivegame.AI.random_player import RandomPlayer
from hivegame.AI.human_player import HumanPlayer
from hivegame.hive_utils import GameStatus

import logging


class Arena(object):

    def __init__(self, player1, player2, environment=None):
        super(Arena, self).__init__()
        if environment is not None:
            self.env = environment
        else:
            self.env = Environment()
        self._player1 = player1
        self._player2 = player2

    def playGame(self):
        self.env.reset_game()  # TODO what?
        env = self.env
        while self.env.check_victory() == GameStatus.UNFINISHED:
            current_player = self._player1 if env.current_player() == "w" else self._player2
            response = current_player.step(env)
            if response == "pass":
                self.env.pass_turn(self.env.hive)
                continue
            if not response:
                break  # e.g. keyboard interrupt
            else:
                try:
                    (piece, coord) = response
                    feedback = env.action_piece_to(piece, coord)
                    current_player.feedback(feedback)
                except ValueError:
                    logging.error("ValueError when unpacking and executing response")

        return env.check_victory()

    def _playNumberOfGames(self, num):
        whiteWon = 0
        blackWon = 0
        draws = 0
        for _ in range(num):
            gameResult = self.playGame()
            if gameResult == GameStatus.WHITE_WIN:
                whiteWon += 1
            elif gameResult == GameStatus.BLACK_WIN:
                blackWon += 1
            elif gameResult == GameStatus.DRAW:
                draws += 1
            else:
                raise ValueError  # Invalid response of environment
        return whiteWon, blackWon, draws

    def playGames(self, num):
        logging.INFO("called")
        # White starts
        (white_won, black_won, draw) = self._playNumberOfGames(num//2)
        self.player1, self.player2 = self.player2, self.player1
        # Black starts
        (black_won2, white_won2, draw2) = self._playNumberOfGames(num//2)
        # Switch it back
        self.player1, self.player2 = self.player2, self.player1
        return white_won + white_won2, black_won + black_won2, draw + draw2


def main():
    # TODO parse options for players
    FORMAT = "[%(filename)s:%(lineno)s - %(funcName)20s() ] %(message)s"
    logging.basicConfig(level=logging.INFO, format=FORMAT)
    # game = Arena(HumanAI(sys.stdin), RandomAI())
    player1 = HumanPlayer(sys.stdin)
    player2 = RandomPlayer()
    logging.info("Start game with the following AIs: {}, {}".format(player1, player2))
    game = Arena(player1, player2)
    game.env.reset_game()
    game.playGame()
    logging.info("Thanks for playing Hive. Have a nice day!")

if __name__ == '__main__':
    sys.exit(main())

#! /usr/bin/env python

import sys
from hivegame.environment import Environment
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
        while self.env.check_victory() == GameStatus.UNFINISHED:
            current_player = self._player1 if self.env.current_player() == "w" else self._player2
            response = current_player.step(self.env)
            if response == "pass":
                self.env.exec_cmd("pass")
                continue
            if isinstance(current_player, HumanPlayer):
                if not response:
                    break
                feedback = self.env.exec_cmd(response)
            else:
                (piece, coord) = response
                feedback = self.env.action_piece_to(piece, coord)
            current_player.feedback(feedback)

        return self.env.check_victory()


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
        logging.INFO("playGames CALLED")
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
    logging.basicConfig(level=logging.INFO)
    # game = Arena(HumanAI(sys.stdin), RandomAI())
    game = Arena(RandomPlayer(), RandomPlayer())
    game.env.reset_game()
    game.playGame()
    print("\nThanks for playing Hive. Have a nice day!")


if __name__ == '__main__':
    sys.exit(main())

#! /usr/bin/env python

import sys
from engine.environment.environment import Environment
from AI.random_player import RandomPlayer
from AI.human_player import HumanPlayer
from AI.hardcoded_player import MiniMaxPlayer
from engine.hive_utils import GameStatus, HiveException, Player


import logging


class Arena(object):

    def __init__(self, player1, player2):
        super(Arena, self).__init__()
        self._player1 = player1
        self._player2 = player2
        self._passed = False

    def playGame(self):
        logging.info("Start a game")
        hive = Environment()
        while hive.check_victory() == GameStatus.UNFINISHED:
            #print(self.env.hive)
            current_player = self._player1 if hive.current_player == "w" else self._player2
            response = current_player.step(hive)
            if response == "pass":
                if self._passed:
                    # both player passed. Ouch
                    logging.error("Both player passed. Ouch.")
                    raise RuntimeError(":(")
                hive.pass_turn()
                self._passed = True
                continue
            else:
                self._passed = False
            if not response:
                logging.debug("AI JUST PASSED")
                break  # e.g. keyboard interrupt
            else:
                try:
                    (piece, coord) = response
                    try:
                        hive.action_piece_to(piece, coord)
                        current_player.feedback(True)
                    except HiveException:
                        current_player.feedback(False)
                except ValueError:
                    logging.error("ValueError when unpacking and executing response")

        return hive.check_victory()

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
                logging.error("Invalid response from environment: {}".format(gameResult))
                raise ValueError
        return whiteWon, blackWon, draws

    def playGames(self, num: int):
        """
        Play a number of games. Half of the game start with player 1 to begin, and player 2 starts the game
        in the other half.

        :param num:
            Number of games to play.
        :return:
            A tuple of two items: The count of winning for each player
        """
        if num == 1:
            self.playGame()
        logging.info(f"Execute {num} games")
        # White starts
        (white_won, black_won, draw) = self._playNumberOfGames(num//2)
        self._player1, self._player2 = self._player2, self._player1
        # Black starts
        (black_won2, white_won2, draw2) = self._playNumberOfGames(num//2)
        # Switch it back
        self._player1, self._player2 = self._player2, self._player1
        return white_won + white_won2, black_won + black_won2, draw + draw2

headless = True

def main():
    # TODO parse options for players
    FORMAT = "[%(filename)s:%(lineno)s - %(funcName)20s() ] %(message)s"
    logging.basicConfig(level=logging.DEBUG, format=FORMAT)
    # game = Arena(HumanAI(sys.stdin), RandomAI())
    player1 = HumanPlayer(sys.stdin)
    player2 = MiniMaxPlayer(Player.BLACK)
    logging.info("Start game with the following AIs: {}, {}".format(player1, player2))
    game = Arena(player1, player2)
    game.playGame()

    logging.info("Thanks for playing Hive. Have a nice day!")


if __name__ == '__main__':
    sys.exit(main())

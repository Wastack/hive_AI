from engine.hive_utils import GameStatus
from engine.hive import Hive


class Environment(Hive):
    _occupied_to_win = 2

    def pass_turn(self):
        self.level.current_player = self._toggle_player(self.level.current_player)  # switch active player

    def check_victory(self) -> int:
        """
        Check the status of the game.
        :return: The status of the game (white wins | black wins | draw | unfinished)
        """
        wq1_pos = self.locate("wQ1")
        bq1_pos = self.locate("bQ1")
        w_lose = wq1_pos and len(self.level.occupied_surroundings(wq1_pos)) >= Environment._occupied_to_win
        b_lose = bq1_pos and len(self.level.occupied_surroundings(bq1_pos)) >= Environment._occupied_to_win
        if w_lose and b_lose:
            return GameStatus.DRAW
        elif w_lose:
            return GameStatus.BLACK_WIN
        elif b_lose:
            return GameStatus.WHITE_WIN
        return GameStatus.UNFINISHED

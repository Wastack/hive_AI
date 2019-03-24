#! /usr/bin/env python

import sys

from hivegame.board import HexBoard
from hivegame.hive import Hive, HiveException
from hivegame.view import HiveView

class Environment:
    """
    Environment controls the game. It contains all the methods to
    create a game, move or put down pieces, ask information about
    current state etc.
    """

    # Current player
    BLACK = 'b'
    WHITE = 'w'

    def __init__(self):
        self.hive = Hive()
        self.view = HiveView(self.hive)
        self.input = sys.stdin
        self.player_pieces = {1: None, 2: None}
        self.logger = None
        self.reset_game()
        self.logger = None

    def ascii_board(self):
        return str(self.view)

    def reset_game(self):
        self.hive.setup()
        self.player_pieces[1] = self.hive.get_unplayed_pieces('w')
        self.player_pieces[2] = self.hive.get_unplayed_pieces('b')
        self.active_player = (2 - (self.hive.turn % 2))
        if self.logger is not None:
            self.logger.close()
        self.logger = open('game.log', 'w')

    def exec_cmd(self, cmd):
        try:
            (cmdType, value) = self.parse_cmd(cmd)
            if cmdType == 'play':
                (actPiece, pointOfContact, refPiece) = value
            if cmdType == 'non_play' and value == 'pass':
                self.hive.action(cmdType, value)
                return True
        except:
            return False

        if pointOfContact is None and self.hive.turn > 1:
            return False

        try:
            direction = None
            if pointOfContact is not None:
                direction = self.poc2direction(pointOfContact)
        except Exception:
            return False

        try:
            self.hive.action('play', (actPiece, refPiece, direction))
        except HiveException:
            return False
        
        return True

    def parse_cmd(self, cmd):
        self.logger.write(cmd+'\n')

        if cmd == 'pass':
            return ('non_play', cmd)
        if len(cmd) == 3:
            movingPiece = cmd
            pointOfContact = None
            refPiece = None
        else:
            if len(cmd) != 8:
                raise Exception("Failed to parse command.")
            movingPiece = cmd[:3]
            pointOfContact = cmd[3:5]
            refPiece = cmd[5:]
        return ('play', (movingPiece, pointOfContact, refPiece))

    def poc2direction(self, pointOfContact):
        "Parse point of contact to a Hive.direction"
        if pointOfContact == '|*':
            return Hive.W
        if pointOfContact == '/*':
            return Hive.NW
        if pointOfContact == '*\\':
            return Hive.NE
        if pointOfContact == '*|':
            return Hive.E
        if pointOfContact == '*/':
            return Hive.SE
        if pointOfContact == '\\*':
            return Hive.SW
        if pointOfContact == '=*':
            return Hive.O
        raise ValueError('Invalid input for point of contact: "%s"' % pointOfContact)

    def check_victory(self):
        return self.hive.check_victory()
    
    def current_player(self):
        return Environment.WHITE if self.hive.turn % 2 > 0 else Environment.BLACK
    
    def unplayed_pieces(self, player):
        return self.hive.get_unplayed_pieces(player)
    
    def get_turn_count(self):
        return self.hive.turn
    
    def get_all_possible_actions(self):
        return self.hive.get_all_possible_actions()
    
    def action_piece_to(self, piece, to_cell):
        try:
            self.hive.action_piece_to(piece, to_cell)
            return True
        except:
            return False
#! /usr/bin/env python

import sys

from hivegame.hive import Hive, HiveException
from hivegame.view import HiveView
from hivegame.utils import Direction


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
        self.logger = None
        self.reset_game()
        self.logger = None

    def ascii_board(self):
        return str(self.view)

    def reset_game(self):
        self.hive.setup()
        if self.logger is not None:
            self.logger.close()
        self.logger = open('game.log', 'w')

    def exec_cmd(self, cmd):
        try:
            (cmdType, value) = self.parse_cmd(cmd)
        except HiveException:
            return False
        if cmdType == 'non_play' and value == 'pass':
            self.hive.action(cmdType, value)
            return True

        if cmdType != 'play':
            return False  # invalid command type

        (actPiece, point_of_contact, ref_piece) = value

        if point_of_contact is None and self.hive.turn > 1:
            return False

        try:
            direction = None
            if point_of_contact is not None:
                direction = self.poc2direction(point_of_contact)
        except ValueError:
            return False

        try:
            self.hive.action('play', (actPiece, ref_piece, direction))
        except HiveException:
            return False
        
        return True

    def parse_cmd(self, cmd):
        self.logger.write(cmd+'\n')

        if cmd == 'pass':
            return 'non_play', cmd
        if len(cmd) == 3:
            moving_piece = cmd
            point_of_contact = None
            ref_piece = None
        else:
            if len(cmd) != 8:
                raise Exception("Failed to parse command.")
            moving_piece = cmd[:3]
            point_of_contact = cmd[3:5]
            ref_piece = cmd[5:]
        return 'play', (moving_piece, point_of_contact, ref_piece)

    @staticmethod
    def poc2direction(point_of_contact):
        """Parse point of contact to a Hive.direction"""""
        if point_of_contact == '|*':
            return Direction.HX_W
        if point_of_contact == '/*':
            return Direction.HX_NW
        if point_of_contact == '*\\':
            return Direction.HX_NE
        if point_of_contact == '*|':
            return Direction.HX_E
        if point_of_contact == '*/':
            return Direction.HX_SE
        if point_of_contact == '\\*':
            return Direction.HX_SW
        if point_of_contact == '=*':
            return Direction.HX_O
        raise ValueError('Invalid input for point of contact: "%s"' % point_of_contact)

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
        except HiveException:
            return False

    def string_representation(self, state):
        return ','.join(str(item) for inner_list in state for item in inner_list)

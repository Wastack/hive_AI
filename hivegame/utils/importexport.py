import json, logging, os
from hivegame.hive import Hive
from hivegame.utils.hexutil import Hex
import ast
import hivegame.pieces.piece_factory as piecefact
from hivegame.project import ROOT_DIR

SAVED_GAME_DIR = "saved_games"

def saved_game_path(file_name: str):
    return os.path.join(ROOT_DIR, SAVED_GAME_DIR, file_name)

def import_hive(file: str) -> Hive:
    data = json.load(open(file, 'r'))

    current_player= data["player"]
    if current_player.lower() != "w" and current_player.lower() != "b":
        logging.error("Wrong format: cannot decode current player")
        raise RuntimeError()
    game = data["game"]
    if not game:
        logging.error("Could not open hive data")
        raise RuntimeError()
    if not isinstance(data, dict):
        logging.error("Wrong format, expected dict")
        raise RuntimeError()
    hive = Hive()
    hive.level.current_player = current_player.lower()
    for hex_str_tuple, v in game.items():
        hex_tuple = ast.literal_eval(hex_str_tuple)
        if not isinstance(hex_tuple, tuple):
            logging.error("Wrong format while deparsing hex tuple")
            raise RuntimeError()
        hexagon = Hex(*hex_tuple)
        if not isinstance(v, list):
            logging.error("Wrong format, expected list")
            raise RuntimeError()
        for piece_str in v:
            hive.level.append_to(piecefact.name_to_piece(piece_str), hexagon)
    return hive

def export_hive(hive:Hive, file:str) -> None:
    data = {}
    data["player"] = hive.current_player
    game = {}
    for hexi, piece_list in hive.level.tiles.items():
        piece_str_list = [str(p) for p in piece_list]
        game[str(tuple(hexi))] = piece_str_list
    data["game"] = game

    with open(file, "w") as write_file:
        json.dump(data, write_file)
from hive_representation import *
from hive import Hive
from hive_utils import HiveException

from copy import deepcopy
import sys

def perft(hive, depth) -> int:
    if depth == 0:
        return 1
    nodes = 0

    move_list = get_all_possible_actions_nonidentical(hive)
    for move in move_list:
        # TODO implement undo move instead of deep copy
        new_hive = deepcopy(hive)
        try:
            new_hive.action_piece_to(deepcopy(move[0]), move[1])
        except Exception as e:
            print("HiveException with message: \"{}\"".format(e))
            print("action was: {}".format(move))
            print("State of map was:")
            print(new_hive)
            raise
        nodes += perft(new_hive, depth - 1)
    return nodes

def main():
    hive = Hive()
    hive.setup()
    DEPTH = 5
    number_of_nodes = perft(hive, DEPTH)
    print("Number of nodes on level {} is: {}".format(DEPTH, number_of_nodes))



if __name__ == '__main__':
    sys.exit(main())

from hive_representation import get_all_possible_actions
from hive import Hive

from copy import deepcopy
import sys

def perft(hive, depth) -> int:
    if depth == 0:
        return 1
    nodes = 0

    move_list = get_all_possible_actions(hive)
    for move in move_list:
        # TODO implement undo move instead of deep copy
        new_hive = deepcopy(hive)
        new_hive.action_piece_to(*move)
        print("------")
        print(new_hive)
        print(hive)
        print("------")
        nodes += perft(new_hive, depth - 1)
    return nodes

def main():
    hive = Hive()
    hive.setup()
    DEPTH = 6
    number_of_nodes = perft(hive, DEPTH)
    print("Number of nodes on level {} is: {}".format(DEPTH, number_of_nodes))



if __name__ == '__main__':
    sys.exit(main())

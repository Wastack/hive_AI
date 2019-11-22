from engine.hive import Hive
from utils import hexutil
from utils.ascii_view import HiveView

def main():
    hive = Hive()

    hive.level.move_or_append_to(hive.get_piece_by_name("wS1"), hexutil.Hex(0, 0))
    hive.level.move_or_append_to(hive.get_piece_by_name("bS1"), hexutil.Hex(2, 0))
    hive.level.move_or_append_to(hive.get_piece_by_name("wQ1"), hexutil.Hex(-1, -1))
    hive.level.move_or_append_to(hive.get_piece_by_name("bQ1"), hexutil.Hex(3, -1))
    hive.level.move_or_append_to(hive.get_piece_by_name("wS2"), hexutil.Hex(-1, 1))
    hive.level.move_or_append_to(hive.get_piece_by_name("bG1"), hexutil.Hex(4, 0))
    hive.level.move_or_append_to(hive.get_piece_by_name("wB1"), hexutil.Hex(-3, 1))
    hive.level.move_or_append_to(hive.get_piece_by_name("bA1"), hexutil.Hex(2, -2))
    hive.level.move_or_append_to(hive.get_piece_by_name("wG1"), hexutil.Hex(-4, 0))
    hive.level.move_or_append_to(hive.get_piece_by_name("bB1"), hexutil.Hex(1, 1))

    view = HiveView(hive.level)
    print(view.to_string())


main()
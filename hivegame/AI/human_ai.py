import logging

class HumanAI:
    def __init__(self, input_stream):
        self._input = input_stream

    def step(self, environment):
        print("Turn: %s" % environment.get_turn_count())
        active_player = environment.current_player()
        print(environment.ascii_board())
        print("pieces available: %s" % sorted(
            environment.unplayed_pieces(active_player).keys()
        ))
        print("player %s play: " % active_player)
        try:
            cmd = self._input.readline()
        except KeyboardInterrupt:
            return None
        return cmd.strip()

    def feedback(self, succeeded):
        if succeeded:
            print()
            print("=" * 79)
            print()
        else:
            print("invalid play!")
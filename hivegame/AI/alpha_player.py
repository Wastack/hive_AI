from hivegame.AI.player import Player

class AlphaPlayer(Player):

    def __init__(self, environment, predictor, args):
        self.environment = environment
        self.predictor = predictor
        self.args = args

    def step(self, environment):
        pass

    def feedback(self, succeeded):
        pass

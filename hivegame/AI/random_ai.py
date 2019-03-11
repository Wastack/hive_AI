import random

class RandomAI:
    def step(self, hive):
        actions = hive.get_all_possible_actions()
        print("DEBUG: length of action space: {}".format(len(actions)))
        if(not actions):
            return None
        return random.choice(tuple(actions))
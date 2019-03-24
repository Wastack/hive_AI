import random
import logging

class RandomAI:
    def step(self, environment):
        actions = environment.get_all_possible_actions()
        logging.info("Length of action space: {}".format(len(actions)))
        if(not actions):
            return None
        return random.choice(tuple(actions))
import random
import logging

class RandomAI:
    def step(self, environment):
        actions = environment.get_all_possible_actions()
        logging.info("RandomAI: Length of action space: {}".format(len(actions)))
        if(not actions):
            return "pass"
        return random.choice(tuple(actions))

    def feedback(self, success):
        if not success:
            logging.warning("RandomAI: Invalid action from " + str(self))
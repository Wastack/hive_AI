from gym import Env
from gym.spaces import Box

from engine.environment.aienvironment import AIEnvironment
from AI.gym.HiveSpace import HiveActionSpace
from AI.random_player import RandomPlayer
from engine.hive_utils import GameStatus
from engine import hive_representation as represent
import numpy as np

class HiveEnv(Env):
    def _state(self):
        return represent.two_dim_representation(represent.get_adjacency_state(self.env.hive))

    def __init__(self):
        super(HiveEnv, self).__init__()
        self.reward_range = (-1., 1.)
        self.env = AIEnvironment()
        self.action_space = HiveActionSpace(self.env.hive)
        self.observation_space = Box(low=0, high=9, shape= (22, 21), dtype=np.uint8)

        # opponent
        self.opponent = RandomPlayer()

    def reset(self):
        self.env = AIEnvironment()
        self.action_space = HiveActionSpace(self.env.hive)
        return np.array(self._state())

    def _reward(self) -> (float, bool):
        reward = 0.
        if self.env.hive.check_victory() == GameStatus.WHITE_WIN:
            reward += 1.
        elif self.env.hive.check_victory() == GameStatus.BLACK_WIN:
            reward -= 1.
        done = self.env.hive.check_victory() != GameStatus.UNFINISHED
        return reward, done

    def step(self, action: int):
        try:
            inner_action = self.env.hive.action_from_vector(action)
            self.env.hive.action_piece_to(*inner_action)
        except:
            return self._state(), -1, 0, {"success" : False}
        (reward, done) = self._reward()
        if not done:
            # opponent's turn
            # Let him play until I have available moves (pass)
            passed = True
            while passed:
                passed = False
                opponent_action = self.opponent.step(self.env)
                if opponent_action == 'pass':
                    self.env.hive.current_player = self.env.hive._toggle_player(self.env.current_player)
                    return self._state(), reward, done, {}
                self.env.hive.action_piece_to(*opponent_action)
                (reward, done) = self._reward()
                if not self.env.get_all_possible_actions():
                    self.env.hive.current_player = self.env.hive._toggle_player(self.env.current_player)
                    passed = True
            return self._state(), reward, done, {}
        return self._state(), reward, done, {}

    def render(self, mode='human'):
        print("Rendering board: \n{}".format(self.env.hive))

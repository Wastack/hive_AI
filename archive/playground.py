import gym

from stable_baselines.common.policies import MlpPolicy, CnnPolicy
from stable_baselines.common.vec_env import DummyVecEnv
from stable_baselines import PPO2, A2C

from AI.gym.HiveEnv import HiveEnv
from AI.random_player import RandomPlayer
from arena import Arena

env = HiveEnv()
env = DummyVecEnv([lambda: env])  # The algorithms require a vectorized environment to run

model = A2C(MlpPolicy, env, verbose=1).learn(total_timesteps=10000)

obs = env.reset()
for i in range(1000):
    action, _states = model.predict(obs)
    obs, rewards, dones, info = env.step(action)
    env.render()

obs = env.reset()

reward_sum = 0.0
randomPlayer = RandomPlayer()
count = 0
while count < 5:
    while True:
        action, _states = model.predict(obs)
        obs, reward, done, info = env.step(action)
        if 'success' in info:
            if not info['success']:
                continue
        reward_sum += reward
        if done:
            count += 1
            break

print("Reward: {}".format(reward_sum))

env.close()
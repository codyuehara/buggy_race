from env import DroneEnv
from stable_baselines3 import PPO
import gymnasium

models_dir ='models/1718436754'

env = DroneEnv()
env.reset()

models_path = f"{models_dir}/30000"
model = PPO.load(models_path, env=env)

episodes = 500

for ep in range(episodes):
    obs, info = env.reset()
    done = False
    while not done:
        action, states = model.predict(obs)
        obs, rewards, done, truncated, info = env.step(action)
        print(rewards)
# train_agents.py
import custom_env
from stable_baselines3 import PPO

if __name__ == "__main__":
    env = custom_env.MultiAgentEnv()

    model = PPO("MlpPolicy", env, verbose=1)
    model.learn(total_timesteps=10000)

    obs, _ = env.reset()
    done = False

    try:
        while not done:
            actions, _ = model.predict(obs)
            obs, reward, done, info = env.step(actions)
            env.render()
    finally:
        env.close()

# train_agents.py
import custom_env_multi_agent
from stable_baselines3 import PPO

if __name__ == "__main__":
    env = custom_env_multi_agent.MultiAgentEnv()
    try:
        model = PPO("MlpPolicy", env, verbose=1)
        model.learn(total_timesteps=10000)

        obs, _ = env.reset()
        done = False

    
        while not done:
            actions, _ = model.predict(obs)
            obs, reward, done, truncated, info = env.step(actions)
            env.render()
    finally:
        env.close()

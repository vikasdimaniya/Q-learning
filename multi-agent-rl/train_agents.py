import custom_env_multi_agent
from stable_baselines3 import DQN

if __name__ == "__main__":
    env = custom_env_multi_agent.MultiAgentEnv()
    try:
        model = DQN("MlpPolicy", env, verbose=1)
        model.learn(total_timesteps=1)
        print("Training finished")

        obs, _ = env.reset()
        done = False

        while not done:
            actions, _ = model.predict(obs)
            obs, reward, done, truncated, info = env.step(actions)
            print(f"Reward: {reward}, Done: {done}, Truncated: {truncated}, Info: {info}")
            env.render()
    finally:
        env.close()

    print("Done")

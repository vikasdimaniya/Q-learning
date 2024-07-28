import custom_env_multi_agent
from stable_baselines3 import DQN

if __name__ == "__main__":
    env_carnivore = custom_env_multi_agent.CarnivoreEnv()
    try:
        model_carnivore = DQN("MlpPolicy", env_carnivore, verbose=1)

        # # Initialize or load the carnivore agent
        # if os.path.exists(carnivore_model_path + ".zip"):
        #     agent_carnivore = DQN.load(carnivore_model_path, env=env_carnivore)
        #     print("Loaded carnivore model")
        # else:
        #     agent_carnivore = DQN("CnnPolicy", env_carnivore, verbose=1)
        # agent_carnivore.learn(total_timesteps=100)
        # agent_carnivore.save(carnivore_model_path)
        # print("Training finished for carnivore")

        # Load the models
        model_carnivore.learn(total_timesteps=1000)
        print("Training finished")

        obs_carnivore, _ = env_carnivore.reset()
        done_carnivore = False

        while not done_carnivore:
            if not done_carnivore:
                actions_carnivore, _ = model_carnivore.predict(obs_carnivore)
                
                obs_carnivore, reward_carnivore, done_carnivore, truncated = env_carnivore.step(actions_carnivore)
                # print(f"Carnivore - Reward: {reward_carnivore}, Done: {done_carnivore}, Truncated: {truncated}, Info: {info}")
                env_carnivore.render()
    finally:
        env_carnivore.close()

    print("Done")

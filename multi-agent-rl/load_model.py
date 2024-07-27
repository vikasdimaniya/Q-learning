import custom_env_multi_agent
from stable_baselines3 import DQN

# Load and use the trained models
if __name__ == "__main__":
    env_carnivore = custom_env_multi_agent.CarnivoreEnv()
    env_herbivore = custom_env_multi_agent.HerbivoreEnv()

    try:
        # Load the models
        loaded_model_carnivore = DQN.load("1_dqn_carnivore_model_10000", env=env_carnivore)
        loaded_model_herbivore = DQN.load("1_dqn_herbivore_model_10000", env=env_herbivore)
        print("Models loaded")

        # Reset the environments
        obs_carnivore, _ = env_carnivore.reset()
        obs_herbivore, _ = env_herbivore.reset()
        done_carnivore = False
        done_herbivore = False

        # Simulate the interaction
        while not done_carnivore:
            if not done_carnivore:
                actions_carnivore, _ = loaded_model_carnivore.predict(obs_carnivore)
                obs_carnivore, reward_carnivore, done_carnivore, truncated, info = env_carnivore.step(actions_carnivore)
                print(f"Carnivore - Reward: {reward_carnivore}, Done: {done_carnivore}, Truncated: {truncated}, Info: {info}")
                env_carnivore.render()
        while not done_herbivore:

            if not done_herbivore:
                actions_herbivore, _ = loaded_model_herbivore.predict(obs_herbivore)
                obs_herbivore, reward_herbivore, done_herbivore, truncated, info = env_herbivore.step(actions_herbivore)
                print(f"Herbivore - Reward: {reward_herbivore}, Done: {done_herbivore}, Truncated: {truncated}, Info: {info}")
                env_herbivore.render()

    finally:
        env_carnivore.close()
        env_herbivore.close()

    print("Done")

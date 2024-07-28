import custom_env_multi_agent
import os
from stable_baselines3 import DQN

# Training the model
if __name__ == "__main__":
    env_carnivore = custom_env_multi_agent.CarnivoreEnv()
    try:
        carnivore_model_path = "dqn_carnivore_model_10000"
        herbivore_model_path = "dqn_herbivore_agent_co_learning"
        model_carnivore = 0
        # Initialize or load the carnivore agent
        if os.path.exists(carnivore_model_path + ".zip"):
            model_carnivore = DQN.load(carnivore_model_path, env=env_carnivore)
            print("Loaded carnivore model")
        else:
            model_carnivore = DQN("CnnPolicy", env_carnivore, verbose=1)
        model_carnivore.learn(total_timesteps=100)
        model_carnivore.save(carnivore_model_path)
        print("Training finished for carnivore")

        # Load the models
        loaded_model_carnivore = DQN.load(carnivore_model_path, env=env_carnivore)
        print("Models loaded")

        # Test and visualize performance with the loaded models
        obs_carnivore, _ = env_carnivore.reset()
        done_carnivore = False

        while not done_carnivore:
            if not done_carnivore:
                actions_carnivore, _ = loaded_model_carnivore.predict(obs_carnivore)
                obs_carnivore, reward_carnivore, done_carnivore, truncated, info = env_carnivore.step(actions_carnivore)
                # print(f"Carnivore - Reward: {reward_carnivore}, Done: {done_carnivore}, Truncated: {truncated}, Info: {info}")
                env_carnivore.render()
    finally:
        env_carnivore.close()

    print("Done")

import os
from stable_baselines3 import DQN
from stable_baselines3.common.vec_env import DummyVecEnv
from multi_agent import MultiAgentEnv  # Ensure correct import of MultiAgentEnv

# Function to create the environment for carnivores
def create_carnivore_env():
    env = MultiAgentEnv(agent_type='carnivore')
    return DummyVecEnv([lambda: env])

# Function to create the environment for herbivores
def create_herbivore_env():
    env = MultiAgentEnv(agent_type='herbivore')
    return DummyVecEnv([lambda: env])

# Unified training function
def train_agent(training_agent, env, timesteps, is_carnivore):
    obs = env.reset()
    action_training, _ = training_agent.predict(obs)
    action = action_training
        
    obs, reward, terminated, truncated = env.step(action)
    training_agent.learn(total_timesteps=timesteps, reset_num_timesteps=False)
    
    if terminated or truncated:
        obs = env.reset()

if __name__ == "__main__":
    carnivore_env = create_carnivore_env()
    herbivore_env = create_herbivore_env()

    carnivore_model_path = "dqn_carnivore_agent_co_learning"
    herbivore_model_path = "dqn_herbivore_agent_co_learning"

    # Initialize or load the carnivore agent
    if os.path.exists(carnivore_model_path + ".zip"):
        carnivore_agent = DQN.load(carnivore_model_path, env=carnivore_env)
        print("Loaded carnivore model")
    else:
        carnivore_agent = DQN("CnnPolicy", carnivore_env, verbose=1, learning_rate=0.001)
        print("Initialized new carnivore model")

    # Initialize or load the herbivore agent
    if os.path.exists(herbivore_model_path + ".zip"):
        herbivore_agent = DQN.load(herbivore_model_path, env=herbivore_env)
        print("Loaded herbivore model")
    else:
        herbivore_agent = DQN("CnnPolicy", herbivore_env, verbose=1, learning_rate=0.001)
        print("Initialized new herbivore model")

    try:
        iterations = 10  # Number of iterations to alternate training
        timesteps_per_iteration = 10  # Timesteps for each training phase

        for i in range(iterations):
            print(f"Iteration {i+1}/{iterations} - Training carnivore agent")
            train_agent(carnivore_agent, carnivore_env, timesteps_per_iteration, is_carnivore=True)
            carnivore_agent.save(carnivore_model_path)

            print(f"Iteration {i+1}/{iterations} - Training herbivore agent")
            train_agent(herbivore_agent, herbivore_env, timesteps_per_iteration, is_carnivore=False)
            herbivore_agent.save(herbivore_model_path)

        print("Training finished")

    finally:
        carnivore_env.close()
        herbivore_env.close()

    print("Done")

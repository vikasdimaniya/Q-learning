import custom_env_multi_agent
from stable_baselines3 import DQN
from stable_baselines3.common.vec_env import DummyVecEnv

# Training the models
if __name__ == "__main__":
    env = custom_env_multi_agent.MultiAgentEnv()
    env = DummyVecEnv([lambda: env])

    try:
        model = DQN("CnnPolicy", env, verbose=1, learning_rate=0.001)

        # Training model
        model.learn(total_timesteps=10)
        model.save("dqn_model_100")
        print("Training finished")

        # Load the model
        loaded_model = DQN.load("dqn_model_100", env=env)
        print("Model loaded")

        # Test and visualize performance with the loaded model
        obs = env.reset()
        done = False

        while not done:
            action, _ = loaded_model.predict(obs)
            obs, total_reward, done, truncated, info = env.step(action)
            
            env.render()
    finally:
        env.close()

    print("Done")

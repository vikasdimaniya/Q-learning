import single_agent_env
from stable_baselines3 import DQN
import pygame

if __name__ == "__main__":
    env_carnivore = single_agent_env.CarnivoreEnv()
    
    try:
        model_carnivore = DQN("CnnPolicy", env_carnivore, verbose=1, device="cuda")
        
        # Training model for carnivores
        total_timesteps = 10000

        # Learn without rendering to avoid resetting the environment
        model_carnivore.learn(total_timesteps=total_timesteps)
        model_carnivore.save("dqn_carnivore_model_10000")
        print("Training finished")

        obs_carnivore, _ = env_carnivore.reset()
        done_carnivore = False

        while not done_carnivore:
            actions_carnivore, _ = model_carnivore.predict(obs_carnivore)
            obs_carnivore, reward_carnivore, done_carnivore, truncated, info = env_carnivore.step(actions_carnivore)
            print(f"Carnivore - Reward: {reward_carnivore}, Done: {done_carnivore}, Truncated: {truncated}, Info: {info}")
            env_carnivore.render()

            # Process PyGame events to keep the window responsive
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    exit()

    finally:
        env_carnivore.close()

    print("Done")

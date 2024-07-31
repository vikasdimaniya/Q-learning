import single_agent_env
from stable_baselines3 import DQN
import pygame
import os

if __name__ == "__main__":
    try:
        env_carnivore = single_agent_env.CarnivoreEnv()
    except Exception as e:
        print("Error initializing environment: ", e)
        exit()
    learning_rate = 0.01
    try:
        carnivore_model_path = "no_decay_attack_only"
        model_carnivore = 0
        if os.path.exists(carnivore_model_path + ".zip"):
            model_carnivore = DQN.load(carnivore_model_path,  env=env_carnivore, learning_rate=learning_rate)
            print("Loaded carnivore model")
        else:
            model_carnivore = DQN("CnnPolicy", env_carnivore, verbose=1, learning_rate=learning_rate)
            print("Initialized new carnivore model")
        
        total_timesteps = 1000000
        # for i in range(0, 100):
        #if(i == 0):
        obs_carnivore, _ = env_carnivore.reset()
        done_carnivore = False
        for j in range(0, 1):
            actions_carnivore, _ = model_carnivore.predict(obs_carnivore)
            obs_carnivore, reward_carnivore, done_carnivore, truncated, info = env_carnivore.step(actions_carnivore)
            # print(f"Carnivore - Reward: {reward_carnivore}, Done: {done_carnivore}, Truncated: {truncated}, Info: {info}")
            env_carnivore.render()

            # Process PyGame events to keep the window responsive
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    exit()
        obs_carnivore, _ = env_carnivore.reset()
        # else:
        model_carnivore.learn(total_timesteps=total_timesteps) # calling learning function again and again resets few variables inside the lib, so don't do it
        model_carnivore.save(carnivore_model_path)

            
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

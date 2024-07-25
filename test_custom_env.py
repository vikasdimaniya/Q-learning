# test_custom_env.py
import time
import custom_env
import pygame

if __name__ == "__main__":
    env = custom_env.CustomEnv()
    obs = env.reset()
    done = False

    try:
        while not done:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    done = True

            action = env.action_space.sample()  # Sample random action
            obs, reward, done, info = env.step(action)
            env.render()
            # time.sleep(0.1)  # Add a small delay to slow down the rendering
    finally:
        env.close()

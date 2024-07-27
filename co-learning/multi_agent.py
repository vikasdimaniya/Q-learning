import gymnasium as gym
from gymnasium import spaces
import pygame
import random
import numpy as np
from map import Map  # Ensure correct import of the Map class

WIDTH, HEIGHT = 400, 400

class MultiAgentEnv(gym.Env):
    def __init__(self, max_steps=1000, agent_type='carnivore'):
        super(MultiAgentEnv, self).__init__()
        self.seed = random.randint(0, 1000000)
        self.simmap = Map(self.seed)
        self.carnivores = [agent for agent in self.simmap.agents if agent.species['diet'] == 'carnivore']
        self.herbivores = [agent for agent in self.simmap.agents if agent.species['diet'] == 'herbivore']
        assert len(self.carnivores) >= 1, "There should be at least one carnivore"

        self.agent_type = agent_type
        self.action_space = spaces.Discrete(8)  # Actions for the specified agent type

        self.observation_space = spaces.Box(low=0, high=255, shape=(WIDTH, HEIGHT, 3), dtype=np.uint8)
        self.screen = pygame.display.set_mode((WIDTH, HEIGHT))
        self.max_steps = max_steps
        self.current_step = 0

    def reset(self, seed=None, options=None):
        self.simmap = Map(self.seed)
        self.carnivores = [agent for agent in self.simmap.agents if agent.species['diet'] == 'carnivore']
        self.herbivores = [agent for agent in self.simmap.agents if agent.species['diet'] == 'herbivore']
        
        assert len(self.carnivores) >= 1, "There should be at least one carnivore"
        self.current_step = 0
        obs = self.render(mode='rgb_array')
        return obs, {}

    def step(self, action):
        if self.agent_type == 'carnivore':
            action_carnivore = action
            action_herbivore = 0  # Default action for herbivores
        else:
            action_herbivore = action
            action_carnivore = 0  # Default action for carnivores

        self.current_step += 1
        self.perform_action(self.carnivores[0], action_carnivore)
        for herbivore in self.herbivores:
            self.perform_action(herbivore, action_herbivore)

        self.simmap.simulate_agents()
        obs = self.render(mode='rgb_array')
        reward_carnivore = self.calculate_carnivore_reward()
        reward_herbivore = self.calculate_herbivore_reward()
        terminated = self.current_step >= self.max_steps  # Termination condition based on max steps
        truncated = False  # Assume no truncation logic is applied
        info = {}

        # Check if all herbivores are dead
        if all(not agent.alive for agent in self.simmap.agents if agent.species == 'herbivore'):
            terminated = True
            reward_carnivore += 100  # Large reward for carnivores if they win

        # Check if the carnivore is dead
        if all(not agent.alive for agent in self.simmap.agents if agent.species == 'carnivore'):
            terminated = True
            reward_carnivore -= 100  # Large penalty for carnivores if they lose

        if self.agent_type == 'carnivore':
            return obs, reward_carnivore, terminated, truncated, info
        else:
            return obs, reward_herbivore, terminated, truncated, info

    def calculate_carnivore_reward(self):
        reward = 0
        for carnivore in self.carnivores:
            nearby_agents = carnivore.find_nearby_agents(10)
            for nearby_agent in nearby_agents:
                if nearby_agent.species['diet'] == 'herbivore' and not nearby_agent.alive:
                    reward += 10  # Positive reward for each herbivore hunted by carnivores
        return reward

    def calculate_herbivore_reward(self):
        reward = 0
        for herbivore in self.herbivores:
            if herbivore.alive:
                reward += 1  # Positive reward for staying alive
        return reward

    def perform_action(self, agent, action):
        if action == 0:
            agent.move_up()
        elif action == 1:
            agent.move_down()
        elif action == 2:
            agent.move_left()
        elif action == 3:
            agent.move_right()
        elif action == 4:
            agent.move_up_left()
        elif action == 5:
            agent.move_up_right()
        elif action == 6:
            agent.move_down_left()
        elif action == 7:
            agent.move_down_right()

        if agent.species['diet'] == 'carnivore':
            self.check_and_eat(agent)

    def check_and_eat(self, agent):
        for herbivore in self.simmap.agents:
            if herbivore.species['diet'] == 'herbivore' and herbivore.alive:
                if herbivore.location == agent.location:
                    herbivore.alive = False  # The herbivore is eaten

    def render(self, mode='human'):
        self.simmap.draw(self.screen)
        self.simmap.draw_agents(self.screen)
        pygame.display.flip()

        if mode == 'rgb_array':
            return pygame.surfarray.array3d(self.screen).swapaxes(0, 1)
        elif mode == 'human':
            return None

    def close(self):
        pygame.quit()

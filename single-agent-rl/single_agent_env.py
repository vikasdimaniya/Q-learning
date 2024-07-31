import pygame
import random
import noise
import math
import numpy as np
import gymnasium as gym
from gymnasium import spaces

# Initialize pygame
pygame.init()
SIZE = 100
# Define constants
WIDTH, HEIGHT = SIZE, SIZE
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
MIN_AGENTS = 1  # Minimum number of agents to spawn
# Define regions
regions = {
    "ocean": {
        "altitude_range": [-1.0, -0.3],
        "color": (0, 105, 148)
    },
    "beach": {
        "altitude_range": [-0.3, -0.2],
        "color": (237, 201, 175)
    },
    "plains": {
        "altitude_range": [-0.2, 0.0],
        "color": (34, 139, 34)
    },
    "forest": {
        "altitude_range": [0.0, 0.2],
        "color": (34, 89, 34)
    },
    "mountain": {
        "altitude_range": [0.2, 0.4],
        "color": (139, 137, 137)
    },
    "snow": {
        "altitude_range": [0.4, 1.0],
        "color": (255, 250, 250)
    }
}

# Define species reference
species_ref = {
    "wolf": {"common_name": "wolf", "diet": "carnivore", "adult_body_mass": 31, "age_at_first_birth": 547, "max_longevity": 354, "home_range": 159.86},
    "moose": {"common_name": "moose", "diet": "herbivore", "adult_body_mass": 461, "age_at_first_birth": 1216, "max_longevity": 324, "home_range": 71.75},
    "beaver": {"common_name": "beaver", "diet": "herbivore", "adult_body_mass": 18, "age_at_first_birth": 220, "max_longevity": 180, "home_range": 5.5}
}

class Map:
    def __init__(self, seed):
        self.size = 50
        self.pixels = SIZE
        self.scale = self.pixels / self.size
        self.noise_scale = 3.0
        self.octaves = 6
        self.persistence = 0.5
        self.lacunarity = 2.0
        self.regen_multiplier = 1500
        self.agents = []
        self.seed = seed
        random.seed(seed)
        self.carnivores = []
        self.init_resource_generation()
        self.init_agents()
        self.world = np.zeros((self.pixels, self.pixels))

        for i in range(self.pixels):
            for j in range(self.pixels):
                nx, ny = i / self.pixels - 0.5, j / self.pixels - 0.5
                self.world[i][j] = noise.pnoise2(nx * self.noise_scale,
                                            ny * self.noise_scale,
                                            octaves=self.octaves,
                                            persistence=self.persistence,
                                            lacunarity=self.lacunarity,
                                            repeatx=self.pixels,
                                            repeaty=self.pixels,
                                            base=self.seed)

    def draw(self, screen):
        for i in range(self.pixels):
            for j in range(self.pixels):
                screen.set_at((i, j), (0, 0, 0))

    # def get_region(self, value):
    #     for region, properties in regions.items():
    #         if properties["altitude_range"][0] <= value < properties["altitude_range"][1]:
    #             return region
    #     return "ocean"

    def init_resource_generation(self):
        self.resource_blocks = []
        for x in range(self.pixels):
            self.resource_blocks.append([])
            for y in range(self.pixels):
                regen_rate = random.random() * self.regen_multiplier
                self.resource_blocks[x].append(ResourceBlock(x, y, regen_rate))

    def init_agents(self):
        for species in species_ref:
            number = MIN_AGENTS
            if species_ref[species]["diet"] == "herbivore":
                number = MIN_AGENTS*25
            self.spawn_agents(species, number)
        self.carnivores = [agent for agent in self.agents if agent.species['diet'] == 'carnivore']
        print(f"Number of carnivores: {len(self.carnivores)}")

    def spawn_agents(self, species, number):
        for _ in range(number):
            agent = Agent(species_ref[species], self)
            location = self.spawn_location()
            agent.location = location
            self.agents.append(agent)

    def spawn_location(self):
        while True:
            x = random.randint(0, self.pixels - 1)
            y = random.randint(0, self.pixels - 1)
            return [x, y]

    def get_noise_value(self, x, y):
        nx, ny = x / self.pixels - 0.5, y / self.pixels - 0.5
        value = noise.pnoise2(nx * self.noise_scale,
                              ny * self.noise_scale,
                              octaves=self.octaves,
                              persistence=self.persistence,
                              lacunarity=self.lacunarity,
                              repeatx=self.pixels,
                              repeaty=self.pixels,
                              base=self.seed)
        return value

    def draw_agents(self, screen):
        for agent in self.agents:
            agent.draw(screen)

    def simulate_agents_and_return_reward(self):
        reward = 0
        for agent in self.carnivores:
            agent_reward = agent.update_and_return_reward()
            reward = agent_reward
        self.agents = [agent for agent in self.agents if agent.alive]
        return reward

class ResourceBlock:
    def __init__(self, x, y, regen_rate):
        self.x = x
        self.y = y
        self.cap = 10000
        self.resources = self.cap
        self.regen_rate = regen_rate

class Agent:
    def __init__(self, species_ref, simmap):
        self.alive = True
        self.safe_to_delete = False
        self.species = species_ref
        self.simmap = simmap
        self.starvation_days = 0
        self.location = [0, 0]
        self.move_distance_in_pixels = 1

    def draw(self, screen):
        if not self.alive:
            pass
        elif self.species['diet'] == "herbivore":
            color = GREEN
            pygame.draw.circle(screen, color, (int(self.location[0]), int(self.location[1])), 2)
        else:
            color = RED
            pygame.draw.circle(screen, color, (int(self.location[0]), int(self.location[1])), 2)

    def update_and_return_reward(self):
        reward = 0
        nearby_agents, nearest_agent_dist = self.find_nearby_agents(10)
        if (len(nearby_agents)==0):
            self.starvation_days += 1
            #reward += -1*nearest_agent_dist
        else:
            for agent in nearby_agents:
                if agent.species['diet'] == "herbivore" and agent.alive:
                    agent.alive = False
                    reward += 100 #- self.starvation_days
                    self.starvation_days = 0
        return reward

    def move_up(self):
        self._move_direction(0, -1)

    def move_down(self):
        self._move_direction(0, 1)

    def move_left(self):
        self._move_direction(-1, 0)

    def move_right(self):
        self._move_direction(1, 0)

    def move_up_left(self):
        self._move_direction(-1, -1)

    def move_up_right(self):
        self._move_direction(1, -1)

    def move_down_left(self):
        self._move_direction(-1, 1)

    def move_down_right(self):
        self._move_direction(1, 1)

    def _move_direction(self, dx, dy):
        if not self.alive:
            return

        new_x = self.location[0] + dx * self.move_distance_in_pixels
        new_y = self.location[1] + dy * self.move_distance_in_pixels

        if new_x < 0 or new_x >= WIDTH or new_y < 0 or new_y >= HEIGHT:
            return

        new_x = max(0, min(WIDTH-1, new_x))
        new_y = max(0, min(HEIGHT-1, new_y))
        
        self.location = [new_x, new_y]

    def find_nearby_agents(self, distance):
        nearby_agents = []
        nearest_agent_dist = 1000000
        for agent in self.simmap.agents:
            if agent is not self and (agent.alive):
                dist = math.sqrt((self.location[0] - agent.location[0])**2 + (self.location[1] - agent.location[1])**2)
                if dist <= distance:
                    nearby_agents.append(agent)
                if dist < nearest_agent_dist:
                    nearest_agent_dist = dist
        return (nearby_agents, nearest_agent_dist)

class CarnivoreEnv(gym.Env):
    def __init__(self):
        super(CarnivoreEnv, self).__init__()
        self.seed = random.randint(0, 1000000)
        self.simmap = Map(self.seed)
        self.carnivores = [agent for agent in self.simmap.agents if agent.species['diet'] == 'carnivore']
        self.herbivores = [agent for agent in self.simmap.agents if agent.species['diet'] == 'herbivore']
        self.action_space = spaces.Discrete(8 * len(self.carnivores))  # 8 possible movement directions for each carnivore agent
        self.observation_space = spaces.Box(low=0, high=255, shape=(WIDTH, HEIGHT, 3), dtype=np.uint8)
        self.screen = pygame.display.set_mode((WIDTH, HEIGHT))
        self.max_steps = 6000
        self.current_step = 0
        self.total_reward = 0

    def reset(self, seed=None, options=None):
        # self.simmap = Map(self.seed) # To keep the same map for all episodes.
        self.simmap = Map(random.randint(0, 1000000))
        self.carnivores = [agent for agent in self.simmap.agents if agent.species['diet'] == 'carnivore']
        with open("no_decay_attack_only_step.txt", "a") as f:
            f.write(str(self.current_step) + "\n")
        self.current_step = 0
        with open("no_decay_attack_only_reward.txt", "a") as f:
            f.write(str(self.total_reward) + "\n")
        self.total_reward = 0
        obs = self.render(mode='rgb_array')
        return obs, {}

    def step(self, action):
        self.current_step += 1

        actions = self.decode_action(action)
        
        for i, agent in enumerate(self.carnivores):
            self.perform_action(agent, actions[i])

        fresh_kill_reward = self.simmap.simulate_agents_and_return_reward()
        obs = self.render(mode='rgb_array')
        reward =0
        
        if self.current_step > 1000:
            reward = (fresh_kill_reward)/(self.current_step/1000)
        else:
            reward = fresh_kill_reward
        # step_penalty = -0.01 * self.current_step  # Add a small penalty for each step
        # reward += step_penalty
        done = False
        truncated = False
        if self.current_step >= self.max_steps:
            done = True
        info = {}
        total_herbivores_alive = 0
        for agent in self.simmap.agents:
            if agent.species['diet'] == 'herbivore' and agent.alive:
                total_herbivores_alive += 1
        if (self.current_step % 100 == 0):
            print(f"Total herbivores alive: {total_herbivores_alive}", f"Step: {self.current_step}", f"Reward: {reward}")
        if total_herbivores_alive == 0:
            done = True
            reward += 1000  # Large bonus for completing the task
        self.total_reward += 50-total_herbivores_alive
        self.total_reward += reward
        return obs, reward, done, truncated, info

    def decode_action(self, action):
        actions = []
        num_agents = len(self.carnivores)
        
        for _ in range(num_agents):
            actions.append(action % 8)
            action //= 8
        return actions

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
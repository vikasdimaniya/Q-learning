# custom_env.py
import pygame
import random
import noise
import math
import numpy as np
import gym
from gym import spaces

# Initialize pygame
pygame.init()

# Define constants
WIDTH, HEIGHT = 400, 400
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
DECAY_RATE = 0.01  # Rate at which dead bodies decay

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
        self.size = 200
        self.pixels = 400
        self.scale = self.pixels / self.size
        self.noise_scale = 3.0
        self.octaves = 6
        self.persistence = 0.5
        self.lacunarity = 2.0
        self.regen_multiplier = 1500
        self.agents = []
        self.seed = seed
        random.seed(seed)
        self.init_resource_generation()
        self.init_agents()

    def draw(self, screen):
        world = np.zeros((self.pixels, self.pixels))

        for i in range(self.pixels):
            for j in range(self.pixels):
                nx, ny = i / self.pixels - 0.5, j / self.pixels - 0.5
                world[i][j] = noise.pnoise2(nx * self.noise_scale,
                                            ny * self.noise_scale,
                                            octaves=self.octaves,
                                            persistence=self.persistence,
                                            lacunarity=self.lacunarity,
                                            repeatx=self.pixels,
                                            repeaty=self.pixels,
                                            base=self.seed)

        for i in range(self.pixels):
            for j in range(self.pixels):
                value = world[i][j]
                region = self.get_region(value)
                color = regions[region]["color"]
                screen.set_at((i, j), color)

    def get_region(self, value):
        for region, properties in regions.items():
            if properties["altitude_range"][0] <= value < properties["altitude_range"][1]:
                return region
        return "ocean"

    def init_resource_generation(self):
        self.resource_blocks = []
        for x in range(self.pixels):
            self.resource_blocks.append([])
            for y in range(self.pixels):
                regen_rate = random.random() * self.regen_multiplier
                self.resource_blocks[x].append(ResourceBlock(x, y, regen_rate))

    def init_agents(self):
        min_agents = 30
        for species in species_ref:
            number = random.randint(min_agents, min_agents * 2)
            if species_ref[species]["diet"] == "herbivore":
                number *= 30
            self.spawn_agents(species, number)

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
            if self.get_region(self.get_noise_value(x, y)) != "ocean":
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

    def simulate_agents(self):
        for agent in self.agents:
            agent.update()
        self.agents = [agent for agent in self.agents if agent.alive or agent.meat_calories > 0]

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
        self.age = 0  # Start all agents at age 0
        self.max_age = self.species['max_longevity'] * 30 * random.uniform(0.5, 1)
        self.starvation_days = 0
        self.location = [0, 0]
        self.sex = "male" if random.random() > 0.5 else "female"
        self.move_distance = math.sqrt(self.species['home_range']) * 0.5
        self.move_distance_in_pixels = self.move_distance * 0.5
        self.last_reproduce = 100000
        self.meat_calories = self.species['adult_body_mass'] * 1500
        self.decay_rate = DECAY_RATE

    def draw(self, screen):
        if not self.alive:
            decay_factor = self.meat_calories / (self.species['adult_body_mass'] * 1500)
            alpha = max(0, int(decay_factor * 255))
            color = (0, 0, 0, alpha)

            temp_surface = pygame.Surface((4, 4), pygame.SRCALPHA)
            temp_surface.set_alpha(alpha)
            temp_surface.fill((0, 0, 0, 0))
            pygame.draw.circle(temp_surface, (0, 0, 0), (2, 2), 2)
            screen.blit(temp_surface, (int(self.location[0]) - 2, int(self.location[1]) - 2))

        elif self.species['diet'] == "herbivore":
            color = GREEN
            pygame.draw.circle(screen, color, (int(self.location[0]), int(self.location[1])), 2)
        else:
            color = RED
            pygame.draw.circle(screen, color, (int(self.location[0]), int(self.location[1])), 2)

    def update(self):
        self.age += 1
        if self.age > self.max_age or self.starvation_days > 30:
            self.alive = False

        if not self.alive:
            self.decay()

        if self.alive:
            if self.species['diet'] == "herbivore":
                self.feed_plant()
            else:
                self.feed_meat()
            if self.age > self.species['age_at_first_birth'] and self.starvation_days < 10 and random.random() < 0.01:
                self.reproduce()
            self.move()

    def move(self):
        if not self.alive:
            return

        for _ in range(10):  # Try up to 10 times to find a valid move
            angle = random.uniform(0, 2 * math.pi)
            new_x = self.location[0] + math.cos(angle) * self.move_distance_in_pixels
            new_y = self.location[1] + math.sin(angle) * self.move_distance_in_pixels

            if new_x < 0 or new_x >= WIDTH:
                continue
            if new_y < 0 or new_y >= HEIGHT:
                continue

            new_x = max(0, min(WIDTH-1, new_x))
            new_y = max(0, min(HEIGHT-1, new_y))

            if self.simmap.get_region(self.simmap.get_noise_value(int(new_x), int(new_y))) != "ocean":
                self.location = [new_x, new_y]
                break

    def find_nearby_agents(self, distance):
        nearby_agents = []
        for agent in self.simmap.agents:
            if agent is not self and (agent.alive or agent.meat_calories > 0):
                dist = math.sqrt((self.location[0] - agent.location[0])**2 + (self.location[1] - agent.location[1])**2)
                if dist <= distance:
                    nearby_agents.append(agent)
        return nearby_agents

    def feed_plant(self):
        pass

    def feed_meat(self):
        nearby_agents = self.find_nearby_agents(10)
        for agent in nearby_agents:
            if agent.species['diet'] == "herbivore" and agent.alive:
                agent.alive = False
                self.starvation_days = 0
                self.meat_calories += agent.meat_calories * 0.5
                break
            elif not agent.alive and agent.meat_calories > 0:
                self.starvation_days = 0
                self.meat_calories += agent.meat_calories * 0.5
                agent.meat_calories *= 0.5
                break
        else:
            self.starvation_days += 1

    def decay(self):
        self.meat_calories -= self.meat_calories * self.decay_rate

    def reproduce(self):
        pass

class CustomEnv(gym.Env):
    def __init__(self):
        super(CustomEnv, self).__init__()
        self.seed = random.randint(0, 1000000)
        self.simmap = Map(self.seed)
        self.action_space = spaces.Discrete(8)  # 8 possible movement directions
        self.observation_space = spaces.Box(low=0, high=255, shape=(WIDTH, HEIGHT, 3), dtype=np.uint8)
        self.screen = pygame.display.set_mode((WIDTH, HEIGHT))

    def reset(self):
        self.simmap = Map(self.seed)
        obs = self.render(mode='rgb_array')
        return obs

    def step(self, action):
        for agent in self.simmap.agents:
            agent.move()  # Move each agent based on their own logic

        self.simmap.simulate_agents()
        obs = self.render(mode='rgb_array')
        reward = 0  # Define your reward logic
        done = False  # Define your termination logic
        info = {}
        return obs, reward, done, info

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

if __name__ == "__main__":
    env = CustomEnv()
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
            time.sleep(0.1)  # Add a small delay to slow down the rendering
    finally:
        env.close()

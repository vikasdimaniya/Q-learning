import gymnasium as gym
from gymnasium import spaces
import numpy as np
import random
import pygame
import noise

WIDTH, HEIGHT = 400, 400
SIZE = 400  # Define the size for the map

# Define regions and species references as they are used in the Map class
regions = {
    "ocean": {"altitude_range": [-1.0, -0.3], "color": (0, 105, 148)},
    "beach": {"altitude_range": [-0.3, -0.2], "color": (237, 201, 175)},
    "plains": {"altitude_range": [-0.2, 0.0], "color": (34, 139, 34)},
    "forest": {"altitude_range": [0.0, 0.2], "color": (34, 89, 34)},
    "mountain": {"altitude_range": [0.2, 0.4], "color": (139, 137, 137)},
    "snow": {"altitude_range": [0.4, 1.0], "color": (255, 250, 250)},
}

species_ref = {
    "wolf": {"common_name": "wolf", "diet": "carnivore", "adult_body_mass": 31, "age_at_first_birth": 547, "max_longevity": 354, "home_range": 159.86},
    "moose": {"common_name": "moose", "diet": "herbivore", "adult_body_mass": 461, "age_at_first_birth": 1216, "max_longevity": 324, "home_range": 71.75},
    "beaver": {"common_name": "beaver", "diet": "herbivore", "adult_body_mass": 18, "age_at_first_birth": 220, "max_longevity": 180, "home_range": 5.5},
}

MIN_AGENTS = 1  # Define the minimum number of agents

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
        self.move_distance = np.sqrt(self.species['home_range']) * 0.5
        self.move_distance_in_pixels = self.move_distance * 0.5
        self.last_reproduce = 100000
        self.meat_calories = self.species['adult_body_mass'] * 1500
        self.decay_rate = 0.01

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
            color = (0, 255, 0)  # Green
            pygame.draw.circle(screen, color, (int(self.location[0]), int(self.location[1])), 2)
        else:
            color = (255, 0, 0)  # Red
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
            angle = random.uniform(0, 2 * np.pi)
            new_x = self.location[0] + np.cos(angle) * self.move_distance_in_pixels
            new_y = self.location[1] + np.sin(angle) * self.move_distance_in_pixels

            if new_x < 0 or new_x >= WIDTH:
                continue
            if new_y < 0 or new_y >= HEIGHT:
                continue

            new_x = max(0, min(WIDTH-1, new_x))
            new_y = max(0, min(HEIGHT-1, new_y))

            if self.simmap.get_region(self.simmap.get_noise_value(int(new_x), int(new_y))) != "ocean":
                self.location = [new_x, new_y]
                break

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

        if self.simmap.get_region(self.simmap.get_noise_value(int(new_x), int(new_y))) != "ocean":
            self.location = [new_x, new_y]

    def find_nearby_agents(self, distance):
        nearby_agents = []
        for agent in self.simmap.agents:
            if agent is not self and (agent.alive or agent.meat_calories > 0):
                dist = np.sqrt((self.location[0] - agent.location[0])**2 + (self.location[1] - agent.location[1])**2)
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

class Map:
    def __init__(self, seed):
        self.size = 200
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
        for species in species_ref:
            number = MIN_AGENTS
            if species_ref[species]["diet"] == "herbivore":
                number = MIN_AGENTS*100
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
                # print (x, y)
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

class MultiAgentEnv(gym.Env):
    def __init__(self, max_steps=1000):
        super(MultiAgentEnv, self).__init__()
        self.seed = random.randint(0, 1000000)
        self.simmap = Map(self.seed)
        self.carnivores = [agent for agent in self.simmap.agents if agent.species['diet'] == 'carnivore']
        self.herbivores = [agent for agent in self.simmap.agents if agent.species['diet'] == 'herbivore']
        assert len(self.carnivores) >= 1, "There should be at least one carnivore"

        # Define composite action space
        self.action_space = spaces.Discrete(8 * 8)  # Combined action space for carnivore and herbivores

        self.observation_space = spaces.Box(low=0, high=255, shape=(WIDTH, HEIGHT, 3), dtype=np.uint8)
        self.screen = pygame.display.set_mode((WIDTH, HEIGHT))
        self.max_steps = max_steps
        self.current_step = 0

    def reset(self, seed=None, options=None):
        self.simmap = Map(self.seed)
        self.carnivores = [agent for agent in self.simmap.agents if agent.species['diet'] == 'carnivore']
        self.herbivores = [agent for agent in self.simmap.agents if agent.species['diet'] == 'herbivore']
        
        # print(f"Carnivores: {len(self.carnivores)}, Herbivores: {len(self.herbivores)}")

        assert len(self.carnivores) >= 1, "There should be at least one carnivore"
        self.current_step = 0
        obs = self.render(mode='rgb_array')
        # print(f"Observation shape (reset): {obs.shape}")  # Add this line
        return obs, {}


    def step(self, action):
        # Decode the combined action
        action_carnivore = action // 8
        action_herbivore = action % 8

        self.current_step += 1
        self.perform_action(self.carnivores[0], action_carnivore)
        for herbivore in self.herbivores:
            self.perform_action(herbivore, action_herbivore)

        self.simmap.simulate_agents()
        obs = self.render(mode='rgb_array')
        reward_carnivore = self.calculate_carnivore_reward()
        reward_herbivore = self.calculate_herbivore_reward()
        done = self.current_step >= self.max_steps  # Termination condition based on max steps
        truncated = False
        info = {}

        # Check if all herbivores are dead
        if all(not agent.alive for agent in self.simmap.agents if agent.species == 'herbivore'):
            done = True
            reward_carnivore += 100  # Large reward for carnivores if they win

        # Check if the carnivore is dead
        if all(not agent.alive for agent in self.simmap.agents if agent.species == 'carnivore'):
            done = True
            reward_carnivore -= 100  # Large penalty for carnivores if they lose

        return obs, (reward_carnivore, reward_herbivore), done, truncated, info



    def calculate_carnivore_reward(self):
        # Reward logic for carnivores:
        reward = 0
        for carnivore in self.carnivores:
            nearby_agents = carnivore.find_nearby_agents(10)
            for nearby_agent in nearby_agents:
                if nearby_agent.species['diet'] == 'herbivore' and not nearby_agent.alive:
                    reward += 10  # Positive reward for each herbivore hunted by carnivores
        return reward

    def calculate_herbivore_reward(self):
        # Reward logic for herbivores:
        reward = 0
        for herbivore in self.herbivores:
            if herbivore.alive:
                reward += 1  # Positive reward for staying alive
        return reward

    def perform_action(self, agent, action):
        # print(f"Performing action {action} for agent {agent.species['common_name']} at location {agent.location}")
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
            
        # Check if the agent moves to a cell with a herbivore and eats it
        if agent.species['diet'] == 'carnivore':
            self.check_and_eat(agent)

    def check_and_eat(self, agent):
        for herbivore in self.simmap.agents:
            if herbivore.species['diet'] == 'herbivore' and herbivore.alive:
                if herbivore.location == agent.location:
                    herbivore.alive = False  # The herbivore is eaten
                    # print(f"Herbivore at location {herbivore.location} eaten by carnivore")


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

import noise
import numpy as np
import random
from resource_block import ResourceBlock
from agent import Agent

SIZE = 400  # Define the size for the map
MIN_AGENTS = 1  # Define the minimum number of agents
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
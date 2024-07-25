import pygame
import random
import noise
import math

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

# Create screen
screen = pygame.display.set_mode((WIDTH, HEIGHT))

# Define data structures
data = []
resource_percentages = []
species_counts = {
    "beaver": [],
    "moose": [],
    "wolf": []
}

class Map:
    def __init__(self, seed):
        self.size = 200
        self.pixels = 400
        self.scale = self.pixels / self.size
        self.noise_scale = 0.03
        self.regen_multiplier = 1500
        self.agents = []
        self.checkerboard_offset = [0, 0]
        self.seed = seed
        random.seed(seed)
        self.init_resource_generation()
        self.init_agents()

    def draw(self):
        for x in range(self.pixels):
            for y in range(self.pixels):
                value = noise.pnoise2(x * self.noise_scale, y * self.noise_scale, octaves=1)
                color_value = int((value + 1) / 2 * 255)
                pygame.draw.rect(screen, (color_value, color_value, color_value), (x, y, 1, 1))

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
            return [x, y]

    def draw_agents(self):
        for agent in self.agents:
            agent.draw()

    def simulate_agents(self):
        for agent in self.agents:
            agent.update()
        # Remove fully decayed agents from the list
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
        self.age = random.uniform(0, self.species['max_longevity'] * 30)  # Ensure age is within lifespan
        self.max_age = self.species['max_longevity'] * 30 * random.uniform(0.5, 1)  # Ensure max_age is a reasonable fraction of the max longevity
        self.starvation_days = 0
        self.location = [0, 0]
        self.sex = "male" if random.random() > 0.5 else "female"
        self.move_distance = math.sqrt(self.species['home_range']) * 0.5  # Reduced speed further
        self.move_distance_in_pixels = self.move_distance * 0.5  # Further reduce speed
        self.last_reproduce = 100000
        self.meat_calories = self.species['adult_body_mass'] * 1500
        self.decay_rate = DECAY_RATE

    def draw(self):
        if not self.alive:
            decay_factor = self.meat_calories / (self.species['adult_body_mass'] * 1500)
            alpha = max(0, int(decay_factor * 255))  # Ensure alpha is between 0 and 255
            color = (0, 0, 0, alpha)

            # Create a temporary surface with alpha channel
            temp_surface = pygame.Surface((4, 4), pygame.SRCALPHA)
            temp_surface.set_alpha(alpha)
            temp_surface.fill((0, 0, 0, 0))  # Fill with transparent color
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
            return  # Dead agents don't move

        angle = random.uniform(0, 2 * math.pi)
        new_x = self.location[0] + math.cos(angle) * self.move_distance_in_pixels
        new_y = self.location[1] + math.sin(angle) * self.move_distance_in_pixels
        
        # Reflect direction if out of bounds
        if new_x < 0 or new_x >= WIDTH:
            angle = math.pi - angle
            new_x = self.location[0] + math.cos(angle) * self.move_distance_in_pixels
        if new_y < 0 or new_y >= HEIGHT:
            angle = -angle
            new_y = self.location[1] + math.sin(angle) * self.move_distance_in_pixels
        
        # Ensure the new position is within bounds
        new_x = max(0, min(WIDTH-1, new_x))
        new_y = max(0, min(HEIGHT-1, new_y))
        
        self.location = [new_x, new_y]

    def find_nearby_agents(self, distance):
        nearby_agents = []
        for agent in self.simmap.agents:
            if agent is not self and (agent.alive or agent.meat_calories > 0):
                dist = math.sqrt((self.location[0] - agent.location[0])**2 + (self.location[1] - agent.location[1])**2)
                if dist <= distance:
                    nearby_agents.append(agent)
        return nearby_agents

    def feed_plant(self):
        # Implement plant feeding logic
        pass

    def feed_meat(self):
        nearby_agents = self.find_nearby_agents(10)  # Define a suitable distance for hunting
        for agent in nearby_agents:
            if agent.species['diet'] == "herbivore" and agent.alive:
                agent.alive = False
                self.starvation_days = 0
                self.meat_calories += agent.meat_calories * 0.5  # Gain half of the herbivore's meat calories
                break
            elif not agent.alive and agent.meat_calories > 0:
                self.starvation_days = 0
                self.meat_calories += agent.meat_calories * 0.5  # Gain half of the decayed meat calories
                agent.meat_calories *= 0.5  # Decay the meat calories
                break
        else:
            self.starvation_days += 1

    def decay(self):
        self.meat_calories -= self.meat_calories * self.decay_rate

    def reproduce(self):
        # Implement reproduction logic
        pass

species_ref = {
    "wolf": {"common_name": "wolf", "diet": "carnivore", "adult_body_mass": 31, "age_at_first_birth": 547, "max_longevity": 354, "home_range": 159.86},
    "moose": {"common_name": "moose", "diet": "herbivore", "adult_body_mass": 461, "age_at_first_birth": 1216, "max_longevity": 324, "home_range": 71.75},
    "beaver": {"common_name": "beaver", "diet": "herbivore", "adult_body_mass": 18, "age_at_first_birth": 220, "max_longevity": 180, "home_range": 5.5}
}

def main():
    seed = random.randint(0, 1000000)
    simmap = Map(seed)
    clock = pygame.time.Clock()
    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
        screen.fill(WHITE)
        simmap.draw()
        simmap.simulate_agents()
        simmap.draw_agents()
        pygame.display.flip()
        clock.tick(60)
    pygame.quit()

if __name__ == "__main__":
    main()

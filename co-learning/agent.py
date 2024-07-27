import random
import numpy as np
import pygame
WIDTH, HEIGHT = 400, 400
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
import pygame
import noise
import numpy as np

# Initialize Pygame
pygame.init()

# Set screen dimensions
width, height = 800, 800
screen = pygame.display.set_mode((width, height))

# Define colors
ocean = (0, 105, 148)
beach = (237, 201, 175)
plains = (34, 139, 34)
forest = (34, 89, 34)
mountains = (139, 137, 137)
snow = (255, 250, 250)

# Generate Perlin noise map
scale = 3.0
octaves = 6
persistence = 0.5
lacunarity = 2.0

world = np.zeros((width, height))

for i in range(width):
    for j in range(height):
        nx, ny = i/width - 0.5, j/height - 0.5
        world[i][j] = noise.pnoise2(nx * scale, 
                                    ny * scale, 
                                    octaves=octaves, 
                                    persistence=persistence, 
                                    lacunarity=lacunarity, 
                                    repeatx=width, 
                                    repeaty=height, 
                                    base=0)

# Map Perlin noise values to colors
for i in range(width):
    for j in range(height):
        value = world[i][j]
        if value < -0.3:
            color = ocean
        elif value < -0.2:
            color = beach
        elif value < 0.0:
            color = plains
        elif value < 0.2:
            color = forest
        elif value < 0.4:
            color = mountains
        else:
            color = snow

        screen.set_at((i, j), color)

# Update display
pygame.display.flip()

# Main loop
running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

# Quit Pygame
pygame.quit()

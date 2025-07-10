import pygame
import random
# Pas d'import relatif nécessaire ici

class Particle:
    def __init__(self, x, y, color):
        self.x = x
        self.y = y
        self.color = color
        self.radius = random.randint(4, 8)
        self.vx = random.uniform(-2, 2)
        self.vy = random.uniform(-3, -1)
        self.life = random.randint(20, 35)
        self.age = 0

    def update(self):
        self.x += self.vx
        self.y += self.vy
        self.vy += 0.15 
        self.radius *= 0.96
        self.age += 1

    def is_alive(self):
        return self.age < self.life and self.radius > 1

    def draw(self, surface):
        if self.is_alive():
            pygame.draw.circle(surface, self.color, (int(self.x), int(self.y)), int(self.radius))


def create_particles(x, y, color, n=8):
    return [Particle(x, y, color) for _ in range(n)] 
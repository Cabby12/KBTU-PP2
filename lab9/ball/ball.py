import pygame

class Ball:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.radius = 25
        self.color = (255, 0, 0)
        self.screen_w = 600
        self.screen_h = 600

    def move(self, dx, dy):
        new_x = self.x + dx
        new_y = self.y + dy

        if new_x - self.radius < 0 or new_x + self.radius > self.screen_w:
            return
        if new_y - self.radius < 0 or new_y + self.radius > self.screen_h:
            return

        self.x = new_x
        self.y = new_y

    def draw(self, screen):
        pygame.draw.circle(screen, self.color, (self.x, self.y), self.radius)

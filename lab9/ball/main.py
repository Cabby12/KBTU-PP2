import pygame
from ball import Ball

pygame.init()

screen = pygame.display.set_mode((600, 600))
pygame.display.set_caption("Moving Ball")
clock = pygame.time.Clock()

ball = Ball(300, 300)

running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_UP:
                ball.move(0, -20)
            elif event.key == pygame.K_DOWN:
                ball.move(0, 20)
            elif event.key == pygame.K_LEFT:
                ball.move(-20, 0)
            elif event.key == pygame.K_RIGHT:
                ball.move(20, 0)

    screen.fill((255, 255, 255))
    ball.draw(screen)
    pygame.display.flip()
    clock.tick(60)

pygame.quit()

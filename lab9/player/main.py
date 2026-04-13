import pygame
from player import MusicPlayer

pygame.init()

screen = pygame.display.set_mode((500, 300))
pygame.display.set_caption("Music Player")
clock = pygame.time.Clock()

player = MusicPlayer("music")

running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_p:
                player.play()
            elif event.key == pygame.K_s:
                player.stop()
            elif event.key == pygame.K_n:
                player.next_track()
            elif event.key == pygame.K_b:
                player.prev_track()
            elif event.key == pygame.K_q:
                running = False

    player.update()
    player.draw(screen)
    pygame.display.flip()
    clock.tick(30)

pygame.quit()

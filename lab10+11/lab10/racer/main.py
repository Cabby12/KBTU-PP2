import pygame, sys, random, time
from pygame.locals import *

pygame.init()

# fps
FPS = 60
FramePerSec = pygame.time.Clock()

# colors
WHITE  = (255, 255, 255)
BLACK  = (0, 0, 0)
RED    = (255, 0, 0)
YELLOW = (255, 215, 0)
GRAY   = (100, 100, 100)
DGRAY  = (80, 80, 80)

# screen and game variables
SCREEN_WIDTH  = 400
SCREEN_HEIGHT = 600
SPEED = 5
SCORE = 0
coins_collected = 0

DISPLAYSURF = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
DISPLAYSURF.fill(WHITE)
pygame.display.set_caption("Racer")

font       = pygame.font.SysFont("Verdana", 60)
font_small = pygame.font.SysFont("Verdana", 18)
game_over_text = font.render("Game Over", True, BLACK)


class Enemy(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        # load enemy car image and scale it
        self.image = pygame.image.load("Enemy.png").convert_alpha()
        self.image = pygame.transform.scale(self.image, (50, 80))
        self.rect  = self.image.get_rect()
        self.rect.center = (random.randint(80, SCREEN_WIDTH - 80), 0)

    def move(self):
        global SCORE
        # move enemy down by SPEED pixels each frame
        self.rect.move_ip(0, SPEED)
        # reset to top when it goes off screen, increment score
        if self.rect.top > SCREEN_HEIGHT:
            SCORE += 1
            self.rect.top = 0
            self.rect.center = (random.randint(80, SCREEN_WIDTH - 80), 0)


class Player(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        # load player car image and scale it
        self.image = pygame.image.load("Player.png").convert_alpha()
        self.image = pygame.transform.scale(self.image, (50, 80))
        self.rect  = self.image.get_rect()
        self.rect.center = (SCREEN_WIDTH // 2, 520)

    def move(self):
        pressed = pygame.key.get_pressed()
        # left/right movement with screen boundary check
        if self.rect.left > 50:
            if pressed[K_LEFT]:
                self.rect.move_ip(-5, 0)
        if self.rect.right < SCREEN_WIDTH - 50:
            if pressed[K_RIGHT]:
                self.rect.move_ip(5, 0)


class Coin(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        # draw coin as yellow circle on transparent surface
        self.image = pygame.Surface((30, 30), pygame.SRCALPHA)
        pygame.draw.circle(self.image, YELLOW, (15, 15), 13)
        pygame.draw.circle(self.image, (0, 0, 0), (15, 15), 13, 2)
        self.rect = self.image.get_rect()
        self.rect.center = (random.randint(70, SCREEN_WIDTH - 70), -10)

    def move(self):
        # coins fall slower than the enemy car
        self.rect.move_ip(0, max(2, int(SPEED // 2)))
        if self.rect.top > SCREEN_HEIGHT:
            self.kill()


# sprite setup
P1 = Player()
E1 = Enemy()

enemies     = pygame.sprite.Group()
enemies.add(E1)
coins       = pygame.sprite.Group()
all_sprites = pygame.sprite.Group()
all_sprites.add(P1, E1)

# increase enemy speed every second (from tutorial part 2)
INC_SPEED  = pygame.USEREVENT + 1
pygame.time.set_timer(INC_SPEED, 1000)

# spawn a coin every 3 seconds
SPAWN_COIN = pygame.USEREVENT + 2
pygame.time.set_timer(SPAWN_COIN, 3000)

# game loop
while True:
    for event in pygame.event.get():
        if event.type == INC_SPEED:
            SPEED += 0.3

        if event.type == SPAWN_COIN:
            # 75% chance a coin spawns each interval
            if random.random() < 0.75:
                c = Coin()
                coins.add(c)
                all_sprites.add(c)

        if event.type == QUIT:
            pygame.quit()
            sys.exit()

    # draw road
    DISPLAYSURF.fill(GRAY)
    pygame.draw.rect(DISPLAYSURF, DGRAY, (50, 0, 300, SCREEN_HEIGHT))
    for y in range(0, SCREEN_HEIGHT, 60):
        pygame.draw.rect(DISPLAYSURF, WHITE, (SCREEN_WIDTH // 2 - 5, y, 10, 35))

    # score top-left
    score_txt = font_small.render("Score: " + str(SCORE), True, WHITE)
    DISPLAYSURF.blit(score_txt, (10, 10))

    # coin count top-right
    coin_txt = font_small.render("Coins: " + str(coins_collected), True, YELLOW)
    DISPLAYSURF.blit(coin_txt, (SCREEN_WIDTH - 120, 10))

    # move and draw all sprites
    for entity in all_sprites:
        entity.move()
        DISPLAYSURF.blit(entity.image, entity.rect)

    # collect coins
    collected = pygame.sprite.spritecollide(P1, coins, True)
    coins_collected += len(collected)

    # player-enemy collision = game over
    if pygame.sprite.spritecollideany(P1, enemies):
        time.sleep(0.5)
        DISPLAYSURF.fill(RED)
        DISPLAYSURF.blit(game_over_text, (30, 220))
        final = font_small.render("Coins: " + str(coins_collected), True, WHITE)
        DISPLAYSURF.blit(final, (160, 320))
        pygame.display.update()
        for entity in all_sprites:
            entity.kill()
        time.sleep(2)
        pygame.quit()
        sys.exit()

    pygame.display.update()
    FramePerSec.tick(FPS)

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
GRAY   = (100, 100, 100)
DGRAY  = (80, 80, 80)

# screen and game variables
SCREEN_WIDTH  = 400
SCREEN_HEIGHT = 600
SPEED         = 5      # enemy fall speed
SCORE         = 0
coins_collected = 0

# enemy speeds up every N coins
COINS_PER_SPEEDUP = 5

DISPLAYSURF = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
DISPLAYSURF.fill(WHITE)
pygame.display.set_caption("Racer")

# fonts
font       = pygame.font.SysFont("Verdana", 60)
font_small = pygame.font.SysFont("Verdana", 18)
game_over_text = font.render("Game Over", True, BLACK)


class Enemy(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        # load the enemy car image
        self.image = pygame.image.load("Enemy.png").convert_alpha()
        self.image = pygame.transform.scale(self.image, (50, 80))
        self.rect  = self.image.get_rect()
        self.rect.center = (random.randint(80, SCREEN_WIDTH - 80), 0)

    def move(self):
        global SCORE
        self.rect.move_ip(0, SPEED)
        # once enemy goes off-screen, reset and add to score
        if self.rect.top > SCREEN_HEIGHT:
            SCORE += 1
            self.rect.top = 0
            self.rect.center = (random.randint(80, SCREEN_WIDTH - 80), 0)


class Player(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        # load the player car image
        self.image = pygame.image.load("Player.png").convert_alpha()
        self.image = pygame.transform.scale(self.image, (50, 80))
        self.rect  = self.image.get_rect()
        self.rect.center = (SCREEN_WIDTH // 2, 520)

    def move(self):
        pressed = pygame.key.get_pressed()
        # boundary-checked left/right movement
        if self.rect.left > 50:
            if pressed[K_LEFT]:
                self.rect.move_ip(-5, 0)
        if self.rect.right < SCREEN_WIDTH - 50:
            if pressed[K_RIGHT]:
                self.rect.move_ip(5, 0)


# coin weights: (value, color, radius, weight)
# weight controls how likely that coin type is to spawn
COIN_TYPES = [
    {"value": 1,  "color": (210, 180, 14),  "radius": 12, "weight": 60},  # common bronze
    {"value": 3,  "color": (180, 180, 180),  "radius": 14, "weight": 30},  # uncommon silver
    {"value": 10, "color": (255, 215, 0),    "radius": 17, "weight": 10},  # rare gold
]

class Coin(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        # pick a coin type based on weight
        weights = [ct["weight"] for ct in COIN_TYPES]
        chosen = random.choices(COIN_TYPES, weights=weights, k=1)[0]

        self.value = chosen["value"]
        color      = chosen["color"]
        r          = chosen["radius"]

        # draw coin as a filled circle on transparent surface
        size = r * 2 + 4
        self.image = pygame.Surface((size, size), pygame.SRCALPHA)
        pygame.draw.circle(self.image, color, (size // 2, size // 2), r)
        # small inner ring to make it look like a coin
        pygame.draw.circle(self.image, (0, 0, 0), (size // 2, size // 2), r, 2)

        self.rect = self.image.get_rect()
        self.rect.center = (random.randint(70, SCREEN_WIDTH - 70), -10)

        # coins fall slower than the enemy
        self.fall_speed = max(2, SPEED // 2)

    def move(self):
        self.rect.move_ip(0, self.fall_speed)
        # remove coin if it goes off the bottom
        if self.rect.top > SCREEN_HEIGHT:
            self.kill()


# sprite setup
P1 = Player()
E1 = Enemy()

enemies    = pygame.sprite.Group()
enemies.add(E1)

coins      = pygame.sprite.Group()

all_sprites = pygame.sprite.Group()
all_sprites.add(P1, E1)

# user event: increase enemy speed every second (tutorial feature)
INC_SPEED = pygame.USEREVENT + 1
pygame.time.set_timer(INC_SPEED, 1000)

# user event: try to spawn a coin every 2.5 seconds
SPAWN_COIN = pygame.USEREVENT + 2
pygame.time.set_timer(SPAWN_COIN, 2500)

# game loop
while True:
    for event in pygame.event.get():
        if event.type == INC_SPEED:
            # gradual speed increase over time (from tutorial part 2/3)
            SPEED += 0.1

        if event.type == SPAWN_COIN:
            # 75% chance a coin actually spawns each interval
            if random.random() < 0.75:
                c = Coin()
                coins.add(c)
                all_sprites.add(c)

        if event.type == QUIT:
            pygame.quit()
            sys.exit()

    # draw road background
    DISPLAYSURF.fill(GRAY)
    pygame.draw.rect(DISPLAYSURF, DGRAY, (50, 0, 300, SCREEN_HEIGHT))
    # road lane markings
    for y in range(0, SCREEN_HEIGHT, 60):
        pygame.draw.rect(DISPLAYSURF, WHITE, (SCREEN_WIDTH // 2 - 5, y, 10, 35))

    # score top-left
    score_txt = font_small.render("Score: " + str(SCORE), True, WHITE)
    DISPLAYSURF.blit(score_txt, (10, 10))

    # coin count top-right
    coin_txt = font_small.render("Coins: " + str(coins_collected), True, (255, 215, 0))
    DISPLAYSURF.blit(coin_txt, (SCREEN_WIDTH - 120, 10))

    # next speed boost indicator
    coins_until = COINS_PER_SPEEDUP - (coins_collected % COINS_PER_SPEEDUP)
    boost_txt = font_small.render("Next boost: " + str(coins_until), True, (200, 200, 200))
    DISPLAYSURF.blit(boost_txt, (10, 32))

    # move and draw all sprites
    for entity in all_sprites:
        entity.move()
        DISPLAYSURF.blit(entity.image, entity.rect)

    # coin collision - collect coins and add their value
    collected = pygame.sprite.spritecollide(P1, coins, True)
    for coin in collected:
        prev = coins_collected
        coins_collected += coin.value
        # check if we crossed a multiple of COINS_PER_SPEEDUP
        if (prev // COINS_PER_SPEEDUP) < (coins_collected // COINS_PER_SPEEDUP):
            SPEED += 1.0  # speed boost when earning N coins

    # player-enemy collision = game over
    if pygame.sprite.spritecollideany(P1, enemies):
        time.sleep(0.5)
        DISPLAYSURF.fill(RED)
        DISPLAYSURF.blit(game_over_text, (30, 220))
        s_txt = font_small.render("Score: " + str(SCORE), True, WHITE)
        c_txt = font_small.render("Coins: " + str(coins_collected), True, (255, 215, 0))
        DISPLAYSURF.blit(s_txt, (160, 310))
        DISPLAYSURF.blit(c_txt, (160, 340))
        pygame.display.update()
        for entity in all_sprites:
            entity.kill()
        time.sleep(2)
        pygame.quit()
        sys.exit()

    pygame.display.update()
    FramePerSec.tick(FPS)

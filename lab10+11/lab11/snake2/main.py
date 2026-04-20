import pygame, random, sys, time

pygame.init()

# grid and screen setup
CELL  = 20
COLS  = 30
ROWS  = 30
WIDTH  = COLS * CELL
HEIGHT = ROWS * CELL

# colors
BLACK  = (0,   0,   0)
WHITE  = (255, 255, 255)
GREEN  = (0,   200, 0)
DGREEN = (0,   140, 0)
GRAY   = (40,  40,  40)
RED    = (200, 0,   0)
YELLOW = (255, 215, 0)
BROWN  = (150, 75,  0)

screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Snake")
clock  = pygame.time.Clock()

font     = pygame.font.SysFont("monospace", 22)
big_font = pygame.font.SysFont("monospace", 40)

# food types: value, color, weight, lifetime in seconds
# weight controls how likely each type is to spawn
# lifetime is how many seconds the food stays before disappearing
FOOD_TYPES = [
    {"value": 1,  "color": (220, 50,  50),  "weight": 60, "lifetime": 10},  # common red, lasts 10s
    {"value": 3,  "color": (80,  80,  220), "weight": 25, "lifetime": 7},   # uncommon blue, lasts 7s
    {"value": 5,  "color": (220, 180, 0),   "weight": 10, "lifetime": 5},   # rare gold, only 5s
    {"value": 10, "color": (180, 0,   180), "weight": 5,  "lifetime": 3},   # very rare purple, only 3s!
]


def draw_grid():
    # draw faint grid lines inside play area
    for x in range(CELL, (COLS - 1) * CELL, CELL):
        pygame.draw.line(screen, GRAY, (x, CELL), (x, (ROWS - 1) * CELL))
    for y in range(CELL, (ROWS - 1) * CELL, CELL):
        pygame.draw.line(screen, GRAY, (CELL, y), ((COLS - 1) * CELL, y))


def draw_walls():
    # draw border walls as brown tiles
    for x in range(COLS):
        pygame.draw.rect(screen, BROWN, (x * CELL, 0, CELL, CELL))
        pygame.draw.rect(screen, BROWN, (x * CELL, (ROWS - 1) * CELL, CELL, CELL))
    for y in range(ROWS):
        pygame.draw.rect(screen, BROWN, (0, y * CELL, CELL, CELL))
        pygame.draw.rect(screen, BROWN, ((COLS - 1) * CELL, y * CELL, CELL, CELL))


def random_food_pos(snake, existing_foods):
    # keep trying positions that aren't on the snake, walls, or other food
    existing_positions = [f["pos"] for f in existing_foods]
    while True:
        x = random.randint(1, COLS - 2)
        y = random.randint(1, ROWS - 2)
        if (x, y) not in snake and (x, y) not in existing_positions:
            return (x, y)


def spawn_food(snake, existing_foods):
    # pick food type by weight
    weights = [ft["weight"] for ft in FOOD_TYPES]
    chosen  = random.choices(FOOD_TYPES, weights=weights, k=1)[0]
    pos     = random_food_pos(snake, existing_foods)
    return {
        "pos":      pos,
        "value":    chosen["value"],
        "color":    chosen["color"],
        "lifetime": chosen["lifetime"],
        "spawned":  time.time(),   # record when it was spawned
    }


def game_loop():
    # snake starts in middle moving right
    snake     = [(COLS // 2, ROWS // 2), (COLS // 2 - 1, ROWS // 2)]
    direction = (1, 0)

    # start with one food on the board
    foods = [spawn_food(snake, [])]

    score = 0
    level = 1
    speed = 8   # ticks per second

    # spawn a new food every 5 seconds
    last_food_spawn = time.time()
    FOOD_SPAWN_INTERVAL = 5

    while True:
        clock.tick(speed)
        now = time.time()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                # arrow key controls, can't reverse direction
                if event.key == pygame.K_UP    and direction != (0,  1): direction = (0, -1)
                elif event.key == pygame.K_DOWN  and direction != (0, -1): direction = (0,  1)
                elif event.key == pygame.K_LEFT  and direction != (1,  0): direction = (-1, 0)
                elif event.key == pygame.K_RIGHT and direction != (-1, 0): direction = (1,  0)

        # move head one cell in current direction
        head = (snake[0][0] + direction[0], snake[0][1] + direction[1])

        # wall collision — hit the border = dead
        if head[0] <= 0 or head[0] >= COLS - 1 or head[1] <= 0 or head[1] >= ROWS - 1:
            return score, level

        # self collision
        if head in snake:
            return score, level

        snake.insert(0, head)

        # check if head landed on any food
        ate = None
        for f in foods:
            if head == f["pos"]:
                ate = f
                break

        if ate:
            score += ate["value"]
            foods.remove(ate)
            # always keep at least one food on the board
            foods.append(spawn_food(snake, foods))

            # level up every 3 score points
            if score % 3 == 0:
                level += 1
                speed += 2  # increase speed each level
        else:
            # no food eaten, remove tail as normal
            snake.pop()

        # remove expired foods (they disappear after their lifetime)
        foods = [f for f in foods if now - f["spawned"] < f["lifetime"]]

        # if all food disappeared, spawn a new one immediately
        if len(foods) == 0:
            foods.append(spawn_food(snake, foods))

        # spawn an additional food every FOOD_SPAWN_INTERVAL seconds (up to 3 max)
        if now - last_food_spawn > FOOD_SPAWN_INTERVAL and len(foods) < 3:
            foods.append(spawn_food(snake, foods))
            last_food_spawn = now

        # --- drawing ---
        screen.fill(BLACK)
        draw_grid()
        draw_walls()

        # draw each food with a timer bar below it showing time remaining
        for f in foods:
            fx, fy = f["pos"]
            elapsed   = now - f["spawned"]
            remaining = max(0, f["lifetime"] - elapsed)
            frac      = remaining / f["lifetime"]  # 1.0 = full, 0.0 = gone

            # food square
            pygame.draw.rect(screen, f["color"], (fx * CELL, fy * CELL, CELL - 1, CELL - 1))

            # timer bar underneath the food cell (green -> red as time runs out)
            bar_color = (int(255 * (1 - frac)), int(255 * frac), 0)
            bar_w     = int((CELL - 2) * frac)
            pygame.draw.rect(screen, bar_color, (fx * CELL + 1, fy * CELL + CELL - 4, bar_w, 3))

        # draw snake (head is brighter green)
        for i, seg in enumerate(snake):
            color = GREEN if i == 0 else DGREEN
            pygame.draw.rect(screen, color, (seg[0] * CELL, seg[1] * CELL, CELL - 1, CELL - 1))

        # hud: score and level
        hud = font.render("Score: " + str(score) + "   Level: " + str(level), True, WHITE)
        screen.blit(hud, (10, 5))

        pygame.display.flip()


def show_game_over(score, level):
    screen.fill(BLACK)
    t1 = big_font.render("Game Over", True, RED)
    t2 = font.render("Score: " + str(score), True, WHITE)
    t3 = font.render("Level: " + str(level), True, YELLOW)
    t4 = font.render("R = restart   Q = quit", True, WHITE)
    screen.blit(t1, (WIDTH // 2 - t1.get_width() // 2, 180))
    screen.blit(t2, (WIDTH // 2 - t2.get_width() // 2, 260))
    screen.blit(t3, (WIDTH // 2 - t3.get_width() // 2, 295))
    screen.blit(t4, (WIDTH // 2 - t4.get_width() // 2, 340))
    pygame.display.flip()

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_r:
                    return
                if event.key == pygame.K_q:
                    pygame.quit()
                    sys.exit()


# keep restarting until player quits
while True:
    score, level = game_loop()
    show_game_over(score, level)

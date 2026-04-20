import pygame, random, sys

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
RED    = (200, 0,   0)
GRAY   = (40,  40,  40)
YELLOW = (255, 215, 0)
BROWN  = (150, 75,  0)

screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Snake")
clock  = pygame.time.Clock()

font     = pygame.font.SysFont("monospace", 22)
big_font = pygame.font.SysFont("monospace", 40)


def draw_grid():
    # faint grid lines inside the play area
    for x in range(CELL, (COLS - 1) * CELL, CELL):
        pygame.draw.line(screen, GRAY, (x, CELL), (x, (ROWS - 1) * CELL))
    for y in range(CELL, (ROWS - 1) * CELL, CELL):
        pygame.draw.line(screen, GRAY, (CELL, y), ((COLS - 1) * CELL, y))


def draw_walls():
    # draw brown border tiles acting as walls
    for x in range(COLS):
        pygame.draw.rect(screen, BROWN, (x * CELL, 0, CELL, CELL))
        pygame.draw.rect(screen, BROWN, (x * CELL, (ROWS - 1) * CELL, CELL, CELL))
    for y in range(ROWS):
        pygame.draw.rect(screen, BROWN, (0, y * CELL, CELL, CELL))
        pygame.draw.rect(screen, BROWN, ((COLS - 1) * CELL, y * CELL, CELL, CELL))


def random_food(snake):
    # keep picking until we find a spot not on the snake or wall
    while True:
        x = random.randint(1, COLS - 2)
        y = random.randint(1, ROWS - 2)
        if (x, y) not in snake:
            return (x, y)


def game_loop():
    # start snake in the middle moving right
    snake     = [(COLS // 2, ROWS // 2), (COLS // 2 - 1, ROWS // 2)]
    direction = (1, 0)
    food      = random_food(snake)

    score = 0
    level = 1
    speed = 8   # ticks per second

    while True:
        clock.tick(speed)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                # change direction, prevent reversing
                if event.key == pygame.K_UP    and direction != (0,  1): direction = (0, -1)
                elif event.key == pygame.K_DOWN  and direction != (0, -1): direction = (0,  1)
                elif event.key == pygame.K_LEFT  and direction != (1,  0): direction = (-1, 0)
                elif event.key == pygame.K_RIGHT and direction != (-1, 0): direction = (1,  0)

        # calculate new head position
        head = (snake[0][0] + direction[0], snake[0][1] + direction[1])

        # wall collision check - hitting the border kills the snake
        if head[0] <= 0 or head[0] >= COLS - 1 or head[1] <= 0 or head[1] >= ROWS - 1:
            return score, level

        # self collision check
        if head in snake:
            return score, level

        snake.insert(0, head)

        # check if food was eaten
        if head == food:
            score += 1
            food = random_food(snake)
            # level up every 3 foods eaten
            if score % 3 == 0:
                level += 1
                speed += 2  # go faster each level
        else:
            snake.pop()  # remove tail if no food eaten

        # draw everything
        screen.fill(BLACK)
        draw_grid()
        draw_walls()

        # draw food as red square
        pygame.draw.rect(screen, RED, (food[0] * CELL, food[1] * CELL, CELL - 1, CELL - 1))

        # draw snake body (head is brighter)
        for i, seg in enumerate(snake):
            color = GREEN if i == 0 else DGREEN
            pygame.draw.rect(screen, color, (seg[0] * CELL, seg[1] * CELL, CELL - 1, CELL - 1))

        # score and level counter at top
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


while True:
    score, level = game_loop()
    show_game_over(score, level)

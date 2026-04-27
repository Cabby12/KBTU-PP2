import pygame, sys, random, time, json, os
from db import setup_db, get_or_create_player, save_session, get_leaderboard, get_personal_best

pygame.init()
pygame.mixer.init()

CELL  = 20
COLS  = 30
ROWS  = 30
WIDTH  = COLS * CELL
HEIGHT = ROWS * CELL

BLACK  = (0,   0,   0)
WHITE  = (255, 255, 255)
GREEN  = (0,   200, 0)
DGREEN = (0,   140, 0)
RED    = (200, 0,   0)
DRED   = (100, 0,   0)
GRAY   = (40,  40,  40)
YELLOW = (255, 215, 0)
BROWN  = (150, 75,  0)
CYAN   = (0,   220, 220)
ORANGE = (255, 140, 0)
PURPLE = (160, 0,   200)

screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Snake")
clock  = pygame.time.Clock()

font     = pygame.font.SysFont("monospace", 20)
big_font = pygame.font.SysFont("monospace", 38, bold=True)
sm_font  = pygame.font.SysFont("monospace", 15)

SETTINGS_FILE = "settings.json"
THEME_PATH    = os.path.join("assets", "theme.mp3")


def load_settings():
    if os.path.exists(SETTINGS_FILE):
        try:
            with open(SETTINGS_FILE) as f:
                return json.load(f)
        except:
            pass
    return {"snake_color": [0,200,0], "grid": True, "sound": True}


def save_settings_file(s):
    with open(SETTINGS_FILE, "w") as f:
        json.dump(s, f, indent=2)


settings = load_settings()


def apply_music():
    if settings.get("sound", True):
        if not pygame.mixer.music.get_busy():
            try:
                pygame.mixer.music.load(THEME_PATH)
                pygame.mixer.music.play(-1)
            except:
                pass
        pygame.mixer.music.set_volume(1.0)
    else:
        pygame.mixer.music.set_volume(0.0)


# try DB connection
db_available = True
try:
    setup_db()
except Exception as e:
    print("DB not available, running offline:", e)
    db_available = False


FOOD_TYPES = [
    {"value":1,  "color":(220,50,50),  "weight":60, "lifetime":10},
    {"value":3,  "color":(80,80,220),  "weight":25, "lifetime":7},
    {"value":5,  "color":(220,180,0),  "weight":10, "lifetime":5},
    {"value":10, "color":(180,0,180),  "weight":5,  "lifetime":3},
]

POWERUP_TYPES = [
    {"kind":"speed",  "color":ORANGE, "label":"SPD"},
    {"kind":"slow",   "color":CYAN,   "label":"SLW"},
    {"kind":"shield", "color":PURPLE, "label":"SHD"},
]


def draw_grid():
    if not settings.get("grid", True):
        return
    for x in range(CELL, (COLS-1)*CELL, CELL):
        pygame.draw.line(screen, GRAY, (x, CELL), (x, (ROWS-1)*CELL))
    for y in range(CELL, (ROWS-1)*CELL, CELL):
        pygame.draw.line(screen, GRAY, (CELL, y), ((COLS-1)*CELL, y))


def draw_walls():
    for x in range(COLS):
        pygame.draw.rect(screen, BROWN, (x*CELL, 0, CELL, CELL))
        pygame.draw.rect(screen, BROWN, (x*CELL, (ROWS-1)*CELL, CELL, CELL))
    for y in range(ROWS):
        pygame.draw.rect(screen, BROWN, (0, y*CELL, CELL, CELL))
        pygame.draw.rect(screen, BROWN, ((COLS-1)*CELL, y*CELL, CELL, CELL))


def random_pos(snake, blocked):
    while True:
        x = random.randint(1, COLS-2)
        y = random.randint(1, ROWS-2)
        if (x,y) not in snake and (x,y) not in blocked:
            return (x,y)


def spawn_food(snake, blocked):
    weights = [f["weight"] for f in FOOD_TYPES]
    chosen  = random.choices(FOOD_TYPES, weights=weights)[0]
    return {**chosen, "pos": random_pos(snake, blocked), "spawned": time.time(), "poison": False}


def spawn_poison(snake, blocked):
    return {"pos": random_pos(snake, blocked), "color": DRED, "value": 0,
            "lifetime": 8, "spawned": time.time(), "poison": True}


def spawn_powerup(snake, blocked):
    t = random.choice(POWERUP_TYPES)
    return {"pos": random_pos(snake, blocked), "kind": t["kind"],
            "color": t["color"], "label": t["label"], "spawned": time.time()}


def place_obstacles(snake, n=5):
    blocked = set(snake)
    obs = []
    for _ in range(n):
        pos = random_pos(snake, blocked)
        obs.append(pos)
        blocked.add(pos)
    return obs


def draw_btn(text, r, active=False):
    col = (80, 80, 160) if active else (40, 40, 40)
    pygame.draw.rect(screen, col, r, border_radius=7)
    pygame.draw.rect(screen, WHITE, r, 2, border_radius=7)
    txt = font.render(text, True, WHITE)
    screen.blit(txt, (r.centerx - txt.get_width()//2, r.centery - txt.get_height()//2))


# ── screens ───────────────────────────────────────────────────

def input_username():
    # always ask for name every launch
    name = ""
    while True:
        apply_music()
        screen.fill(BLACK)
        screen.blit(big_font.render("SNAKE", True, GREEN), (WIDTH//2-70, 80))
        screen.blit(font.render("Enter your name:", True, WHITE), (WIDTH//2-100, 210))
        screen.blit(font.render(name + "|", True, YELLOW), (WIDTH//2-80, 250))
        screen.blit(sm_font.render("Press Enter to continue", True, GRAY), (WIDTH//2-100, 300))
        pygame.display.flip()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit(); sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN and name.strip():
                    return name.strip()
                elif event.key == pygame.K_BACKSPACE:
                    name = name[:-1]
                elif event.unicode.isprintable() and len(name) < 15:
                    name += event.unicode


def main_menu():
    buttons = ["Play", "Leaderboard", "Settings", "Quit"]
    while True:
        apply_music()
        screen.fill(BLACK)
        screen.blit(big_font.render("SNAKE", True, GREEN), (WIDTH//2-70, 60))
        rects = []
        for i, b in enumerate(buttons):
            r = pygame.Rect(WIDTH//2-80, 170+i*70, 160, 48)
            draw_btn(b, r)
            rects.append((r, b))
        pygame.display.flip()
        for event in pygame.event.get():
            if event.type == pygame.QUIT: pygame.quit(); sys.exit()
            if event.type == pygame.MOUSEBUTTONDOWN:
                for r, b in rects:
                    if r.collidepoint(event.pos): return b


def leaderboard_screen():
    rows = get_leaderboard() if db_available else []
    while True:
        screen.fill(BLACK)
        screen.blit(font.render("TOP 10 SCORES", True, YELLOW), (WIDTH//2-90, 15))
        if not rows:
            screen.blit(sm_font.render("No scores yet / DB offline", True, GRAY), (WIDTH//2-110, 80))
        for i, row in enumerate(rows):
            txt = sm_font.render(f"{i+1}. {row[0]}  {row[1]}pts  Lv{row[2]}  {row[3]}", True, WHITE)
            screen.blit(txt, (15, 55+i*40))
        back = pygame.Rect(WIDTH//2-50, HEIGHT-55, 100, 38)
        draw_btn("Back", back)
        pygame.display.flip()
        for event in pygame.event.get():
            if event.type == pygame.QUIT: pygame.quit(); sys.exit()
            if event.type == pygame.MOUSEBUTTONDOWN:
                if back.collidepoint(event.pos): return
            if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE: return


def settings_screen():
    global settings
    while True:
        screen.fill(BLACK)
        screen.blit(font.render("Settings", True, YELLOW), (WIDTH//2-55, 20))

        gr = pygame.Rect(WIDTH//2-80, 80, 160, 38)
        pygame.draw.rect(screen, GRAY, gr, border_radius=6)
        pygame.draw.rect(screen, GREEN if settings["grid"] else RED, gr, 2, border_radius=6)
        screen.blit(sm_font.render("Grid: " + ("ON" if settings["grid"] else "OFF"), True, WHITE), (gr.x+35, gr.y+10))

        sr = pygame.Rect(WIDTH//2-80, 140, 160, 38)
        pygame.draw.rect(screen, GRAY, sr, border_radius=6)
        pygame.draw.rect(screen, GREEN if settings["sound"] else RED, sr, 2, border_radius=6)
        screen.blit(sm_font.render("Sound: " + ("ON" if settings["sound"] else "OFF"), True, WHITE), (sr.x+28, sr.y+10))

        screen.blit(sm_font.render("Snake color:", True, WHITE), (WIDTH//2-70, 200))
        color_opts = [("Green",[0,200,0]), ("Blue",[0,100,200]), ("Yellow",[220,200,0])]
        crects = []
        for i, (cname, cval) in enumerate(color_opts):
            r = pygame.Rect(20+i*110, 225, 100, 32)
            sel = settings["snake_color"] == cval
            pygame.draw.rect(screen, tuple(cval), r, border_radius=5)
            pygame.draw.rect(screen, WHITE if sel else GRAY, r, 3 if sel else 1, border_radius=5)
            screen.blit(sm_font.render(cname, True, BLACK), (r.x+10, r.y+8))
            crects.append((r, cval))

        save_r = pygame.Rect(WIDTH//2-70, HEIGHT-65, 140, 42)
        draw_btn("Save & Back", save_r)

        pygame.display.flip()
        for event in pygame.event.get():
            if event.type == pygame.QUIT: pygame.quit(); sys.exit()
            if event.type == pygame.MOUSEBUTTONDOWN:
                if gr.collidepoint(event.pos):
                    settings["grid"] = not settings["grid"]
                if sr.collidepoint(event.pos):
                    settings["sound"] = not settings["sound"]
                    apply_music()
                for r, cval in crects:
                    if r.collidepoint(event.pos):
                        settings["snake_color"] = cval
                if save_r.collidepoint(event.pos):
                    save_settings_file(settings)
                    return


def game_over_screen(score, level, personal_best):
    buttons = ["Retry", "Main Menu"]
    while True:
        screen.fill(BLACK)
        screen.blit(big_font.render("GAME OVER", True, RED), (WIDTH//2-130, 80))
        screen.blit(font.render(f"Score: {score}", True, WHITE), (WIDTH//2-60, 175))
        screen.blit(font.render(f"Level: {level}", True, YELLOW), (WIDTH//2-55, 210))
        screen.blit(font.render(f"Best:  {personal_best}", True, CYAN), (WIDTH//2-55, 245))
        rects = []
        for i, b in enumerate(buttons):
            r = pygame.Rect(WIDTH//2-80, 310+i*70, 160, 48)
            draw_btn(b, r)
            rects.append((r, b))
        pygame.display.flip()
        for event in pygame.event.get():
            if event.type == pygame.QUIT: pygame.quit(); sys.exit()
            if event.type == pygame.MOUSEBUTTONDOWN:
                for r, b in rects:
                    if r.collidepoint(event.pos): return b


# ── game loop ────────────────────────────────────────────────

def game_loop(personal_best):
    snake     = [(COLS//2, ROWS//2), (COLS//2-1, ROWS//2)]
    direction = (1, 0)
    score     = 0
    level     = 1
    speed     = 8
    shield    = False

    foods     = [spawn_food(snake, set())]
    poison    = None
    powerup   = None
    active_pu = None
    pu_end    = 0
    obstacles = []

    last_food_spawn  = time.time()
    last_poison_spawn = time.time()
    last_pu_spawn    = time.time()

    snake_color = tuple(settings.get("snake_color", [0,200,0]))
    head_color  = tuple(min(255, c+60) for c in snake_color)

    while True:
        base_speed = speed
        if active_pu == "slow":  base_speed = max(3, speed-4)
        if active_pu == "speed": base_speed = speed + 3
        clock.tick(base_speed)
        now = time.time()

        for event in pygame.event.get():
            if event.type == pygame.QUIT: pygame.quit(); sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_UP    and direction != (0,1):  direction = (0,-1)
                elif event.key == pygame.K_DOWN  and direction != (0,-1): direction = (0,1)
                elif event.key == pygame.K_LEFT  and direction != (1,0):  direction = (-1,0)
                elif event.key == pygame.K_RIGHT and direction != (-1,0): direction = (1,0)

        head = (snake[0][0]+direction[0], snake[0][1]+direction[1])

        hit_wall = head[0]<=0 or head[0]>=COLS-1 or head[1]<=0 or head[1]>=ROWS-1
        hit_obs  = head in obstacles
        hit_self = head in snake

        if hit_wall or hit_obs or hit_self:
            if shield:
                shield = False
                head   = snake[0]
            else:
                return score, level

        snake.insert(0, head)
        blocked = set(snake) | set(obstacles)

        ate = None
        for f in foods:
            if head == f["pos"]:
                ate = f
                break

        if ate:
            if ate["poison"]:
                for _ in range(2):
                    if len(snake) > 1: snake.pop()
                if len(snake) <= 1:
                    return score, level
            else:
                score += ate["value"]
                if score > 0 and score % 3 == 0:
                    level += 1
                    speed += 2
                    if level >= 3:
                        obstacles = place_obstacles(snake, level)
            foods.remove(ate)
            foods.append(spawn_food(snake, blocked))
        else:
            snake.pop()

        if poison and head == poison["pos"]:
            for _ in range(2):
                if len(snake) > 1: snake.pop()
            if len(snake) <= 1:
                return score, level
            poison = None

        if powerup and head == powerup["pos"]:
            active_pu = powerup["kind"]
            pu_end    = now + 5
            if active_pu == "shield":
                shield    = True
                active_pu = None
            powerup = None

        if active_pu and now > pu_end:
            active_pu = None

        foods = [f for f in foods if now - f["spawned"] < f["lifetime"]]
        if len(foods) == 0:
            foods.append(spawn_food(snake, blocked))
        if now - last_food_spawn > 5 and len(foods) < 3:
            foods.append(spawn_food(snake, blocked))
            last_food_spawn = now

        if now - last_poison_spawn > 7 and poison is None and random.random() < 0.5:
            poison = spawn_poison(snake, blocked)
            last_poison_spawn = now
        if poison and now - poison["spawned"] > poison["lifetime"]:
            poison = None

        if now - last_pu_spawn > 10 and powerup is None:
            powerup = spawn_powerup(snake, blocked)
            last_pu_spawn = now
        if powerup and now - powerup["spawned"] > 8:
            powerup = None

        screen.fill(BLACK)
        draw_grid()
        draw_walls()

        for o in obstacles:
            pygame.draw.rect(screen, BROWN, (o[0]*CELL, o[1]*CELL, CELL-1, CELL-1))
            pygame.draw.rect(screen, (100,50,0), (o[0]*CELL, o[1]*CELL, CELL-1, CELL-1), 2)

        for f in foods:
            fx, fy = f["pos"]
            frac   = max(0, 1 - (now-f["spawned"])/f["lifetime"])
            pygame.draw.rect(screen, f["color"], (fx*CELL, fy*CELL, CELL-1, CELL-1))
            bar_col = (int(255*(1-frac)), int(255*frac), 0)
            pygame.draw.rect(screen, bar_col, (fx*CELL+1, fy*CELL+CELL-4, int((CELL-2)*frac), 3))

        if poison:
            px, py = poison["pos"]
            pygame.draw.rect(screen, DRED, (px*CELL, py*CELL, CELL-1, CELL-1))
            pygame.draw.rect(screen, RED,  (px*CELL, py*CELL, CELL-1, CELL-1), 2)

        if powerup:
            ppx, ppy = powerup["pos"]
            pygame.draw.rect(screen, powerup["color"], (ppx*CELL, ppy*CELL, CELL-1, CELL-1))
            lbl = sm_font.render(powerup["label"], True, BLACK)
            screen.blit(lbl, (ppx*CELL+2, ppy*CELL+3))

        for i, seg in enumerate(snake):
            col = head_color if i == 0 else snake_color
            pygame.draw.rect(screen, col, (seg[0]*CELL, seg[1]*CELL, CELL-1, CELL-1))

        hud = font.render(f"Score:{score}  Lv:{level}  Best:{personal_best}", True, WHITE)
        screen.blit(hud, (5, 3))
        if shield:
            screen.blit(sm_font.render("SHIELD", True, CYAN), (WIDTH-75, 3))
        if active_pu:
            rem = max(0, pu_end - now)
            screen.blit(sm_font.render(f"{active_pu.upper()}:{rem:.1f}s", True, ORANGE), (WIDTH-110, 20))

        pygame.display.flip()


# ── entry point ───────────────────────────────────────────────

apply_music()
username  = input_username()
player_id = None
pb        = 0

if db_available:
    try:
        player_id = get_or_create_player(username)
        pb = get_personal_best(player_id)
    except:
        db_available = False

while True:
    action = main_menu()
    if action == "Play":
        score, level = game_loop(pb)
        if db_available and player_id:
            try:
                save_session(player_id, score, level)
                pb = get_personal_best(player_id)
            except:
                pass
        result = game_over_screen(score, level, pb)
        if result == "Main Menu":
            continue
    elif action == "Leaderboard":
        leaderboard_screen()
    elif action == "Settings":
        settings_screen()
        settings = load_settings()
        apply_music()
    elif action == "Quit":
        pygame.quit()
        sys.exit()

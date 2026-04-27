import pygame, sys, random, time, os
from pygame.locals import *
from persistence import load_settings, save_settings, load_leaderboard, save_score

pygame.init()
pygame.mixer.init()

FPS = 60
SCREEN_WIDTH  = 500
SCREEN_HEIGHT = 650
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Racer")
clock = pygame.time.Clock()

WHITE  = (255,255,255)
BLACK  = (0,0,0)
RED    = (220,30,30)
YELLOW = (255,215,0)
GRAY   = (100,100,100)
DGRAY  = (70,70,70)
GREEN  = (0,200,0)
ORANGE = (255,140,0)
CYAN   = (0,220,220)

font_big   = pygame.font.SysFont("verdana", 48, bold=True)
font_med   = pygame.font.SysFont("verdana", 26)
font_small = pygame.font.SysFont("verdana", 18)

settings = load_settings()

ROAD_LEFT  = 60
ROAD_RIGHT = SCREEN_WIDTH - 60
ROAD_W     = ROAD_RIGHT - ROAD_LEFT

DIFF = {"easy": 0.6, "normal": 1.0, "hard": 1.5}

THEME_PATH = os.path.join("assets", "theme.mp3")


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


def get_diff():
    return DIFF.get(settings.get("difficulty", "normal"), 1.0)


def make_car(color, w=50, h=80):
    surf = pygame.Surface((w, h), pygame.SRCALPHA)
    pygame.draw.rect(surf, color, (5, 5, w-10, h-10), border_radius=6)
    pygame.draw.rect(surf, (150,210,255), (10, 15, w-20, 22), border_radius=3)
    pygame.draw.rect(surf, (30,30,30), (2, 8, 12, 16), border_radius=2)
    pygame.draw.rect(surf, (30,30,30), (w-14, 8, 12, 16), border_radius=2)
    pygame.draw.rect(surf, (30,30,30), (2, h-24, 12, 16), border_radius=2)
    pygame.draw.rect(surf, (30,30,30), (w-14, h-24, 12, 16), border_radius=2)
    pygame.draw.rect(surf, (255,255,150), (8, 5, 14, 8))
    pygame.draw.rect(surf, (255,255,150), (w-22, 5, 14, 8))
    return surf


class Player(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.image = make_car(tuple(settings.get("car_color", [0,0,200])))
        self.rect  = self.image.get_rect(center=(SCREEN_WIDTH//2, 550))
        self.shield = False
        self.nitro  = False
        self.nitro_end = 0
        self.hp = 3
        self.slowed_until = 0

    def move(self):
        slowed = time.time() < self.slowed_until
        spd = 2 if slowed else (7 if self.nitro and time.time() < self.nitro_end else 5)
        keys = pygame.key.get_pressed()
        if keys[K_LEFT]  and self.rect.left  > ROAD_LEFT:  self.rect.x -= spd
        if keys[K_RIGHT] and self.rect.right < ROAD_RIGHT: self.rect.x += spd

    def update(self):
        self.move()
        if self.nitro and time.time() > self.nitro_end:
            self.nitro = False


class Enemy(pygame.sprite.Sprite):
    def __init__(self, speed):
        super().__init__()
        self.image = make_car(RED)
        self.rect  = self.image.get_rect(center=(random.randint(ROAD_LEFT+30, ROAD_RIGHT-30), -50))
        self.speed = speed

    def update(self):
        self.rect.y += self.speed
        if self.rect.top > SCREEN_HEIGHT:
            self.kill()


class Coin(pygame.sprite.Sprite):
    TYPES = [
        {"value":1,  "color":(210,180,14), "r":10, "w":60},
        {"value":3,  "color":(180,180,180),"r":12, "w":28},
        {"value":10, "color":(255,215,0),  "r":14, "w":10},
        {"value":2,  "color":(255,100,0),  "r":11, "w":2},
    ]
    def __init__(self, speed):
        super().__init__()
        t = random.choices(self.TYPES, weights=[c["w"] for c in self.TYPES])[0]
        self.value = t["value"]
        sz = t["r"]*2+4
        self.image = pygame.Surface((sz,sz), pygame.SRCALPHA)
        pygame.draw.circle(self.image, t["color"], (sz//2,sz//2), t["r"])
        pygame.draw.circle(self.image, BLACK, (sz//2,sz//2), t["r"], 2)
        self.rect = self.image.get_rect(center=(random.randint(ROAD_LEFT+20, ROAD_RIGHT-20), -20))
        self.speed = max(2, speed//2)

    def update(self):
        self.rect.y += self.speed
        if self.rect.top > SCREEN_HEIGHT:
            self.kill()


class Obstacle(pygame.sprite.Sprite):
    def __init__(self, speed):
        super().__init__()
        kind = random.choice(["oil", "bump", "barrier"])
        self.image = pygame.Surface((50, 20), pygame.SRCALPHA)
        if kind == "oil":
            pygame.draw.ellipse(self.image, (20,20,80,200), (0,0,50,20))
            self.lethal = False
        elif kind == "bump":
            pygame.draw.rect(self.image, (120,80,40), (0,5,50,10), border_radius=3)
            self.lethal = False
        else:
            pygame.draw.rect(self.image, (200,50,50), (0,0,50,20), border_radius=2)
            self.lethal = True
        self.rect = self.image.get_rect(center=(random.randint(ROAD_LEFT+30, ROAD_RIGHT-30), -20))
        self.speed = speed

    def update(self):
        self.rect.y += self.speed
        if self.rect.top > SCREEN_HEIGHT:
            self.kill()


class PowerUp(pygame.sprite.Sprite):
    TYPES   = ["nitro", "shield", "repair"]
    COLORS  = {"nitro": ORANGE, "shield": CYAN, "repair": GREEN}

    def __init__(self, speed):
        super().__init__()
        self.kind = random.choice(self.TYPES)
        self.image = pygame.Surface((32,32), pygame.SRCALPHA)
        pygame.draw.circle(self.image, self.COLORS[self.kind], (16,16), 14)
        pygame.draw.circle(self.image, WHITE, (16,16), 14, 2)
        lbl = font_small.render(self.kind[0].upper(), True, BLACK)
        self.image.blit(lbl, (16-lbl.get_width()//2, 16-lbl.get_height()//2))
        self.rect = self.image.get_rect(center=(random.randint(ROAD_LEFT+20, ROAD_RIGHT-20), -20))
        self.speed = max(2, speed//2)
        self.spawned = time.time()

    def update(self):
        self.rect.y += self.speed
        if self.rect.top > SCREEN_HEIGHT or time.time() - self.spawned > 8:
            self.kill()


road_offset = 0

def draw_road():
    global road_offset
    screen.fill(GRAY)
    pygame.draw.rect(screen, DGRAY, (ROAD_LEFT, 0, ROAD_W, SCREEN_HEIGHT))
    road_offset = (road_offset + 5) % 80
    for y in range(-80 + road_offset, SCREEN_HEIGHT, 80):
        pygame.draw.rect(screen, WHITE, (SCREEN_WIDTH//2-5, y, 10, 50))


def btn(text, r, selected=False):
    col = (100,100,180) if selected else DGRAY
    pygame.draw.rect(screen, col, r, border_radius=8)
    pygame.draw.rect(screen, WHITE, r, 2, border_radius=8)
    txt = font_med.render(text, True, WHITE)
    screen.blit(txt, (r.centerx - txt.get_width()//2, r.centery - txt.get_height()//2))


def input_username():
    # always ask for name on launch
    name = ""
    while True:
        apply_music()
        screen.fill(BLACK)
        t = font_big.render("RACER", True, YELLOW)
        screen.blit(t, (SCREEN_WIDTH//2 - t.get_width()//2, 100))
        screen.blit(font_med.render("Enter your name:", True, WHITE), (SCREEN_WIDTH//2-110, 220))
        box_surf = font_med.render(name + "|", True, YELLOW)
        screen.blit(box_surf, (SCREEN_WIDTH//2 - box_surf.get_width()//2, 260))
        hint = font_small.render("Press Enter to continue", True, GRAY)
        screen.blit(hint, (SCREEN_WIDTH//2 - hint.get_width()//2, 320))
        pygame.display.flip()
        for event in pygame.event.get():
            if event.type == QUIT:
                pygame.quit(); sys.exit()
            if event.type == KEYDOWN:
                if event.key == K_RETURN and name.strip():
                    return name.strip()
                elif event.key == K_BACKSPACE:
                    name = name[:-1]
                elif event.unicode.isprintable() and len(name) < 15:
                    name += event.unicode


def main_menu():
    buttons = ["Play", "Leaderboard", "Settings", "Quit"]
    while True:
        apply_music()
        screen.fill(BLACK)
        t = font_big.render("RACER", True, YELLOW)
        screen.blit(t, (SCREEN_WIDTH//2 - t.get_width()//2, 80))
        rects = []
        for i, b in enumerate(buttons):
            r = pygame.Rect(SCREEN_WIDTH//2-100, 200+i*70, 200, 50)
            btn(b, r)
            rects.append((r, b))
        pygame.display.flip()
        for event in pygame.event.get():
            if event.type == QUIT:
                pygame.quit(); sys.exit()
            if event.type == MOUSEBUTTONDOWN:
                for r, b in rects:
                    if r.collidepoint(event.pos):
                        return b


def leaderboard_screen():
    lb = load_leaderboard()
    while True:
        screen.fill(BLACK)
        screen.blit(font_med.render("TOP 10", True, YELLOW), (SCREEN_WIDTH//2-50, 20))
        for i, entry in enumerate(lb[:10]):
            row = f"{i+1}. {entry['name']}  {entry['score']}pts  {entry['distance']}m  {entry['coins']} coins"
            txt = font_small.render(row, True, WHITE)
            screen.blit(txt, (20, 70+i*42))
        back = pygame.Rect(SCREEN_WIDTH//2-60, SCREEN_HEIGHT-60, 120, 40)
        btn("Back", back)
        pygame.display.flip()
        for event in pygame.event.get():
            if event.type == QUIT: pygame.quit(); sys.exit()
            if event.type == MOUSEBUTTONDOWN:
                if back.collidepoint(event.pos): return
            if event.type == KEYDOWN and event.key == K_ESCAPE: return


def settings_screen():
    global settings
    colors = {"Blue":(0,0,200), "Red":(200,0,0), "Green":(0,180,0), "White":(230,230,230)}
    diffs  = ["easy", "normal", "hard"]
    while True:
        screen.fill(BLACK)
        screen.blit(font_med.render("Settings", True, YELLOW), (SCREEN_WIDTH//2-60, 20))

        sr = pygame.Rect(50, 80, 220, 40)
        pygame.draw.rect(screen, DGRAY, sr, border_radius=6)
        pygame.draw.rect(screen, GREEN if settings["sound"] else RED, sr, 2, border_radius=6)
        screen.blit(font_small.render("Sound: " + ("ON" if settings["sound"] else "OFF"), True, WHITE), (65, 92))

        screen.blit(font_small.render("Car color:", True, WHITE), (50, 140))
        crects = []
        for i, (cname, cval) in enumerate(colors.items()):
            r = pygame.Rect(50+i*90, 165, 80, 30)
            col = (100,100,180) if list(cval) == settings["car_color"] else DGRAY
            pygame.draw.rect(screen, col, r, border_radius=5)
            pygame.draw.rect(screen, WHITE, r, 1, border_radius=5)
            screen.blit(font_small.render(cname, True, WHITE), (r.x+5, r.y+7))
            crects.append((r, list(cval)))

        screen.blit(font_small.render("Difficulty:", True, WHITE), (50, 220))
        drects = []
        for i, d in enumerate(diffs):
            r = pygame.Rect(50+i*120, 245, 110, 30)
            col = (100,100,180) if d == settings["difficulty"] else DGRAY
            pygame.draw.rect(screen, col, r, border_radius=5)
            pygame.draw.rect(screen, WHITE, r, 1, border_radius=5)
            screen.blit(font_small.render(d.capitalize(), True, WHITE), (r.x+10, r.y+7))
            drects.append((r, d))

        save_r = pygame.Rect(SCREEN_WIDTH//2-80, SCREEN_HEIGHT-70, 160, 45)
        btn("Save & Back", save_r)

        pygame.display.flip()
        for event in pygame.event.get():
            if event.type == QUIT: pygame.quit(); sys.exit()
            if event.type == MOUSEBUTTONDOWN:
                if sr.collidepoint(event.pos):
                    settings["sound"] = not settings["sound"]
                    apply_music()
                for r, cval in crects:
                    if r.collidepoint(event.pos):
                        settings["car_color"] = cval
                for r, d in drects:
                    if r.collidepoint(event.pos):
                        settings["difficulty"] = d
                if save_r.collidepoint(event.pos):
                    save_settings(settings)
                    return


def game_over_screen(username, score, distance, coins):
    save_score(username, score, distance, coins)
    buttons = ["Retry", "Main Menu"]
    while True:
        screen.fill(BLACK)
        screen.blit(font_big.render("GAME OVER", True, RED), (SCREEN_WIDTH//2-130, 80))
        screen.blit(font_med.render(f"Score: {score}", True, WHITE), (SCREEN_WIDTH//2-70, 180))
        screen.blit(font_med.render(f"Distance: {int(distance)}m", True, WHITE), (SCREEN_WIDTH//2-90, 220))
        screen.blit(font_med.render(f"Coins: {coins}", True, YELLOW), (SCREEN_WIDTH//2-60, 260))
        rects = []
        for i, b in enumerate(buttons):
            r = pygame.Rect(SCREEN_WIDTH//2-100, 340+i*70, 200, 50)
            btn(b, r)
            rects.append((r, b))
        pygame.display.flip()
        for event in pygame.event.get():
            if event.type == QUIT: pygame.quit(); sys.exit()
            if event.type == MOUSEBUTTONDOWN:
                for r, b in rects:
                    if r.collidepoint(event.pos):
                        return b


def play_game(username):
    player = Player()
    all_sprites = pygame.sprite.Group(player)
    enemies   = pygame.sprite.Group()
    coins     = pygame.sprite.Group()
    obstacles = pygame.sprite.Group()
    powerups  = pygame.sprite.Group()

    diff     = get_diff()
    speed    = 5 * diff
    score    = 0
    coins_n  = 0
    distance = 0.0
    active_powerup = None
    powerup_end    = 0
    powerup_label  = ""

    INC_SPEED   = USEREVENT + 1
    SPAWN_ENEMY = USEREVENT + 2
    SPAWN_COIN  = USEREVENT + 3
    SPAWN_OBS   = USEREVENT + 4
    SPAWN_POWER = USEREVENT + 5

    pygame.time.set_timer(INC_SPEED,   1000)
    pygame.time.set_timer(SPAWN_ENEMY, int(1200/diff))
    pygame.time.set_timer(SPAWN_COIN,  2000)
    pygame.time.set_timer(SPAWN_OBS,   int(3000/diff))
    pygame.time.set_timer(SPAWN_POWER, 6000)

    while True:
        clock.tick(FPS)
        distance += speed * 0.01

        for event in pygame.event.get():
            if event.type == QUIT: pygame.quit(); sys.exit()
            if event.type == KEYDOWN and event.key == K_ESCAPE:
                return score, distance, coins_n
            if event.type == INC_SPEED:
                speed = min(speed + 0.2*diff, 20)
                score += 1
            if event.type == SPAWN_ENEMY:
                e = Enemy(speed)
                enemies.add(e); all_sprites.add(e)
            if event.type == SPAWN_COIN:
                if random.random() < 0.75:
                    c = Coin(speed)
                    coins.add(c); all_sprites.add(c)
            if event.type == SPAWN_OBS:
                if random.random() < 0.6:
                    o = Obstacle(speed)
                    obstacles.add(o); all_sprites.add(o)
            if event.type == SPAWN_POWER:
                if len(powerups) == 0 and random.random() < 0.5:
                    p = PowerUp(speed)
                    powerups.add(p); all_sprites.add(p)

        if active_powerup and time.time() > powerup_end:
            active_powerup = None
            player.nitro   = False

        all_sprites.update()

        for c in pygame.sprite.spritecollide(player, coins, True):
            coins_n += c.value
            score   += c.value

        for p in pygame.sprite.spritecollide(player, powerups, True):
            active_powerup = p.kind
            powerup_end    = time.time() + 5
            powerup_label  = p.kind.upper()
            if p.kind == "nitro":
                player.nitro     = True
                player.nitro_end = powerup_end
            elif p.kind == "shield":
                player.shield    = True
            elif p.kind == "repair":
                player.hp = min(3, player.hp + 1)
                active_powerup = None  # repair is instant, no timer needed

        for o in pygame.sprite.spritecollide(player, obstacles, True):
            if o.lethal and not player.shield:
                player.hp -= 1
                if player.hp <= 0:
                    return score, distance, coins_n
            elif o.lethal and player.shield:
                player.shield = False
            else:
                # oil spill or bump — slow player movement for 2 seconds
                player.slowed_until = time.time() + 2

        for hit in pygame.sprite.spritecollide(player, enemies, True):
            if player.shield:
                player.shield = False
            else:
                player.hp -= 1
                if player.hp <= 0:
                    return score, distance, coins_n

        draw_road()
        all_sprites.draw(screen)

        screen.blit(font_small.render(f"Score: {score}", True, WHITE), (5, 5))
        screen.blit(font_small.render(f"Coins: {coins_n}", True, YELLOW), (SCREEN_WIDTH-120, 5))
        screen.blit(font_small.render(f"Dist: {int(distance)}m", True, WHITE), (5, 25))

        # draw HP hearts in top-right corner
        for i in range(3):
            col = RED if i < player.hp else DGRAY
            pygame.draw.circle(screen, col, (SCREEN_WIDTH - 20 - i*22, 45), 8)

        if active_powerup:
            rem = max(0, powerup_end - time.time())
            screen.blit(font_small.render(f"{powerup_label}: {rem:.1f}s", True, CYAN), (SCREEN_WIDTH//2-50, 5))
        if player.shield:
            screen.blit(font_small.render("SHIELD", True, CYAN), (SCREEN_WIDTH//2-30, 25))
        if time.time() < player.slowed_until:
            rem = player.slowed_until - time.time()
            screen.blit(font_small.render(f"SLOW {rem:.1f}s", True, (180,100,255)), (SCREEN_WIDTH//2-40, 45))

        pygame.display.flip()


# entry point - ask for name every launch
apply_music()
username = input_username()

while True:
    action = main_menu()
    if action == "Play":
        score, dist, coins_n = play_game(username)
        result = game_over_screen(username, score, dist, coins_n)
        if result == "Retry":
            score, dist, coins_n = play_game(username)
            result = game_over_screen(username, score, dist, coins_n)
    elif action == "Leaderboard":
        leaderboard_screen()
    elif action == "Settings":
        settings_screen()
    elif action == "Quit":
        pygame.quit()
        sys.exit()

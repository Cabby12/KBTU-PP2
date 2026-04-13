import pygame
import datetime
import math
import os

def draw_hand(screen, img, cx, cy, angle_deg, length):
    scaled = pygame.transform.scale(img, (30, length))
    rotated = pygame.transform.rotate(scaled, -angle_deg)
    # pivot is bottom center of the original image
    # after rotation we need to offset so bottom center lands on (cx, cy)
    orig_w, orig_h = 30, length
    angle_rad = math.radians(angle_deg)
    # bottom center of unrotated image relative to its top-left
    pivot_x = orig_w / 2
    pivot_y = orig_h
    # where that point ends up after rotation
    cos_a = math.cos(angle_rad)
    sin_a = math.sin(angle_rad)
    rx = cos_a * (pivot_x - orig_w/2) - sin_a * (pivot_y - orig_h/2)
    ry = sin_a * (pivot_x - orig_w/2) + cos_a * (pivot_y - orig_h/2)
    rw, rh = rotated.get_size()
    blit_x = cx - (rw/2 + rx)
    blit_y = cy - (rh/2 + ry)
    screen.blit(rotated, (int(blit_x), int(blit_y)))

def run_clock():
    screen = pygame.display.set_mode((400, 450))
    pygame.display.set_caption("mickey clock")
    font = pygame.font.SysFont("arial", 30)
    clock = pygame.time.Clock()

    img_path = os.path.join(os.path.dirname(__file__), "images", "mickey_hand.png")
    hand_img = pygame.image.load(img_path).convert_alpha()

    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        now = datetime.datetime.now()
        hours = now.hour % 12
        minutes = now.minute
        seconds = now.second

        screen.fill((200, 200, 200))

        cx, cy = 200, 210
        pygame.draw.circle(screen, (0, 0, 0), (cx, cy), 150, 3)

        hour_angle = hours * 30 + minutes * 0.5
        draw_hand(screen, hand_img, cx, cy, hour_angle, 80)

        min_angle = minutes * 6
        draw_hand(screen, hand_img, cx, cy, min_angle, 110)

        sec_angle = seconds * 6
        pygame.draw.line(screen, (255, 0, 0), (cx, cy),
            (cx + int(130 * math.sin(math.radians(sec_angle))),
             cy - int(130 * math.cos(math.radians(sec_angle)))), 2)

        txt = font.render(f"{now.hour:02}:{minutes:02}:{seconds:02}", True, (0, 0, 0))
        screen.blit(txt, (200 - txt.get_width()//2, 380))

        pygame.display.flip()
        clock.tick(1)

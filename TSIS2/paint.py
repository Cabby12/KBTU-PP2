import pygame
import sys
import math
import datetime
from tools import (draw_line, draw_rect, draw_square, draw_circle,
                   draw_right_triangle, draw_eq_triangle, draw_rhombus, flood_fill)

pygame.init()

WIDTH, HEIGHT = 900, 650
TOOLBAR_H = 80
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Paint")
clock = pygame.time.Clock()

PALETTE = [
    (0,0,0),(255,255,255),(255,0,0),(0,200,0),(0,0,255),
    (255,165,0),(255,255,0),(128,0,128),(0,255,255),(255,105,180),
]

# tool constants
TOOL_PENCIL = "pencil"
TOOL_LINE   = "line"
TOOL_RECT   = "rect"
TOOL_SQUARE = "square"
TOOL_CIRCLE = "circle"
TOOL_RTRI   = "rtri"
TOOL_ETRI   = "etri"
TOOL_RHOMBUS = "rhombus"
TOOL_FILL   = "fill"
TOOL_ERASER = "eraser"
TOOL_TEXT   = "text"

TOOLS = [
    (TOOL_PENCIL,  "Pencil"),
    (TOOL_LINE,    "Line"),
    (TOOL_RECT,    "Rect"),
    (TOOL_SQUARE,  "Square"),
    (TOOL_CIRCLE,  "Circle"),
    (TOOL_RTRI,    "RTri"),
    (TOOL_ETRI,    "EqTri"),
    (TOOL_RHOMBUS, "Rhombus"),
    (TOOL_FILL,    "Fill"),
    (TOOL_ERASER,  "Eraser"),
    (TOOL_TEXT,    "Text"),
]

# brush sizes: small=2, medium=5, large=10
BRUSH_SIZES = [2, 5, 10]

current_tool  = TOOL_PENCIL
current_color = (0, 0, 0)
brush_idx     = 1  # medium by default
drawing       = False
start_pos     = None
last_pos      = None

# text tool state
text_active   = False
text_pos      = None
text_buffer   = ""

canvas = pygame.Surface((WIDTH, HEIGHT - TOOLBAR_H))
canvas.fill((255, 255, 255))

font      = pygame.font.SysFont("monospace", 11)
text_font = pygame.font.SysFont("arial", 20)

TOOL_BTN_W = 62
SHAPE_TOOLS = {TOOL_LINE, TOOL_RECT, TOOL_SQUARE, TOOL_CIRCLE, TOOL_RTRI, TOOL_ETRI, TOOL_RHOMBUS}


def brush_size():
    return BRUSH_SIZES[brush_idx]


def canvas_pos(pos):
    return (pos[0], pos[1] - TOOLBAR_H)


def draw_toolbar():
    pygame.draw.rect(screen, (210, 210, 210), (0, 0, WIDTH, TOOLBAR_H))

    # tool buttons row 1 (first 6)
    for i, (t, label) in enumerate(TOOLS[:6]):
        x = 2 + i * (TOOL_BTN_W + 2)
        col = (160, 160, 255) if t == current_tool else (190, 190, 190)
        pygame.draw.rect(screen, col, (x, 3, TOOL_BTN_W, 22), border_radius=3)
        pygame.draw.rect(screen, (80,80,80), (x, 3, TOOL_BTN_W, 22), 1, border_radius=3)
        screen.blit(font.render(label, True, (0,0,0)), (x+4, 9))

    # tool buttons row 2 (rest)
    for i, (t, label) in enumerate(TOOLS[6:]):
        x = 2 + i * (TOOL_BTN_W + 2)
        col = (160, 160, 255) if t == current_tool else (190, 190, 190)
        pygame.draw.rect(screen, col, (x, 28, TOOL_BTN_W, 22), border_radius=3)
        pygame.draw.rect(screen, (80,80,80), (x, 28, TOOL_BTN_W, 22), 1, border_radius=3)
        screen.blit(font.render(label, True, (0,0,0)), (x+4, 34))

    # color swatches
    for i, c in enumerate(PALETTE):
        x = 400 + i * 28
        pygame.draw.rect(screen, c, (x, 5, 24, 24))
        thick = 3 if c == current_color else 1
        pygame.draw.rect(screen, (0,0,0) if c == current_color else (80,80,80), (x, 5, 24, 24), thick)

    # brush size buttons
    labels = ["S(1)", "M(2)", "L(3)"]
    for i, lbl in enumerate(labels):
        x = 400 + i * 50
        col = (160,160,255) if brush_idx == i else (190,190,190)
        pygame.draw.rect(screen, col, (x, 32, 45, 20), border_radius=3)
        pygame.draw.rect(screen, (80,80,80), (x, 32, 45, 20), 1, border_radius=3)
        screen.blit(font.render(lbl, True, (0,0,0)), (x+5, 37))

    # brush preview
    pygame.draw.circle(screen, current_color, (WIDTH - 30, 40), min(brush_size(), 18))

    # hint
    hint = font.render("Ctrl+S=save  1/2/3=brush size", True, (80,80,80))
    screen.blit(hint, (WIDTH - 200, 5))


def handle_toolbar_click(pos):
    global current_tool, current_color, brush_idx

    # row 1
    for i, (t, _) in enumerate(TOOLS[:6]):
        x = 2 + i * (TOOL_BTN_W + 2)
        if x <= pos[0] <= x + TOOL_BTN_W and 3 <= pos[1] <= 25:
            current_tool = t
            return True

    # row 2
    for i, (t, _) in enumerate(TOOLS[6:]):
        x = 2 + i * (TOOL_BTN_W + 2)
        if x <= pos[0] <= x + TOOL_BTN_W and 28 <= pos[1] <= 50:
            current_tool = t
            return True

    # color swatches
    for i, c in enumerate(PALETTE):
        x = 400 + i * 28
        if x <= pos[0] <= x + 24 and 5 <= pos[1] <= 29:
            current_color = c
            return True

    # brush size
    for i in range(3):
        x = 400 + i * 50
        if x <= pos[0] <= x + 45 and 32 <= pos[1] <= 52:
            brush_idx = i
            return True

    return False


def dispatch_shape(surface, p1, p2):
    sz = brush_size()
    if current_tool == TOOL_LINE:     draw_line(surface, current_color, p1, p2, sz)
    elif current_tool == TOOL_RECT:   draw_rect(surface, current_color, p1, p2, sz)
    elif current_tool == TOOL_SQUARE: draw_square(surface, current_color, p1, p2, sz)
    elif current_tool == TOOL_CIRCLE: draw_circle(surface, current_color, p1, p2, sz)
    elif current_tool == TOOL_RTRI:   draw_right_triangle(surface, current_color, p1, p2, sz)
    elif current_tool == TOOL_ETRI:   draw_eq_triangle(surface, current_color, p1, p2, sz)
    elif current_tool == TOOL_RHOMBUS: draw_rhombus(surface, current_color, p1, p2, sz)


running = True
while running:
    clock.tick(60)

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        # keyboard shortcuts
        if event.type == pygame.KEYDOWN:
            # brush size shortcuts
            if event.key == pygame.K_1: brush_idx = 0
            elif event.key == pygame.K_2: brush_idx = 1
            elif event.key == pygame.K_3: brush_idx = 2

            # ctrl+s save
            if event.key == pygame.K_s and pygame.key.get_mods() & pygame.KMOD_CTRL:
                fname = "canvas_" + datetime.datetime.now().strftime("%Y%m%d_%H%M%S") + ".png"
                pygame.image.save(canvas, fname)
                print("saved:", fname)

            # text tool input
            if text_active:
                if event.key == pygame.K_RETURN:
                    surf = text_font.render(text_buffer, True, current_color)
                    canvas.blit(surf, text_pos)
                    text_active = False
                    text_buffer = ""
                    text_pos = None
                elif event.key == pygame.K_ESCAPE:
                    text_active = False
                    text_buffer = ""
                    text_pos = None
                elif event.key == pygame.K_BACKSPACE:
                    text_buffer = text_buffer[:-1]
                else:
                    if event.unicode and event.unicode.isprintable():
                        text_buffer += event.unicode

        if event.type == pygame.MOUSEBUTTONDOWN:
            pos = event.pos
            if pos[1] < TOOLBAR_H:
                handle_toolbar_click(pos)
            else:
                cp = canvas_pos(pos)

                if current_tool == TOOL_FILL:
                    flood_fill(canvas, cp, current_color)

                elif current_tool == TOOL_TEXT:
                    text_active = True
                    text_pos    = cp
                    text_buffer = ""

                elif current_tool == TOOL_ERASER:
                    drawing  = True
                    last_pos = cp
                    pygame.draw.circle(canvas, (255,255,255), cp, brush_size() * 3)

                elif current_tool == TOOL_PENCIL:
                    drawing  = True
                    last_pos = cp
                    pygame.draw.circle(canvas, current_color, cp, brush_size())

                else:
                    drawing   = True
                    start_pos = cp

        if event.type == pygame.MOUSEBUTTONUP:
            if drawing and event.pos[1] >= TOOLBAR_H:
                cp = canvas_pos(event.pos)
                if current_tool in SHAPE_TOOLS and start_pos:
                    dispatch_shape(canvas, start_pos, cp)
            drawing   = False
            start_pos = None
            last_pos  = None

        if event.type == pygame.MOUSEMOTION:
            if drawing and event.pos[1] >= TOOLBAR_H:
                cp = canvas_pos(event.pos)
                if current_tool == TOOL_PENCIL and last_pos:
                    pygame.draw.line(canvas, current_color, last_pos, cp, brush_size())
                    last_pos = cp
                elif current_tool == TOOL_ERASER and last_pos:
                    pygame.draw.line(canvas, (255,255,255), last_pos, cp, brush_size() * 3)
                    last_pos = cp

    # render
    screen.fill((255,255,255))
    screen.blit(canvas, (0, TOOLBAR_H))

    # shape preview while dragging
    if drawing and start_pos and current_tool in SHAPE_TOOLS:
        cp = canvas_pos(pygame.mouse.get_pos())
        preview = canvas.copy()
        dispatch_shape(preview, start_pos, cp)
        screen.blit(preview, (0, TOOLBAR_H))

    # text cursor preview
    if text_active and text_pos:
        preview_surf = text_font.render(text_buffer + "|", True, current_color)
        screen.blit(preview_surf, (text_pos[0], text_pos[1] + TOOLBAR_H))

    draw_toolbar()
    pygame.display.flip()

pygame.quit()

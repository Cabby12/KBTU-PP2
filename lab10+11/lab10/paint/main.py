import pygame
import sys
import math

pygame.init()

WIDTH, HEIGHT = 800, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Paint")
clock = pygame.time.Clock()

TOOLBAR_H = 50

# color palette
PALETTE = [
    (0,   0,   0),
    (255, 255, 255),
    (255, 0,   0),
    (0,   200, 0),
    (0,   0,   255),
    (255, 165, 0),
    (255, 255, 0),
    (128, 0,   128),
    (0,   255, 255),
    (255, 105, 180),
]

# tool names
TOOL_PEN    = "pen"
TOOL_RECT   = "rect"
TOOL_CIRCLE = "circle"
TOOL_ERASER = "eraser"

# state
current_color = (0, 0, 0)
current_tool  = TOOL_PEN
brush_size    = 4
drawing       = False
start_pos     = None

# canvas surface - drawing happens here, separate from toolbar
canvas = pygame.Surface((WIDTH, HEIGHT - TOOLBAR_H))
canvas.fill((255, 255, 255))

font = pygame.font.SysFont("monospace", 13)

TOOLS = [
    (TOOL_PEN,    "Pen"),
    (TOOL_RECT,   "Rect"),
    (TOOL_CIRCLE, "Circle"),
    (TOOL_ERASER, "Eraser"),
]
TOOL_BTN_W = 75


def draw_toolbar():
    pygame.draw.rect(screen, (215, 215, 215), (0, 0, WIDTH, TOOLBAR_H))

    # tool buttons
    for i, (t, label) in enumerate(TOOLS):
        x   = 4 + i * (TOOL_BTN_W + 3)
        col = (170, 170, 255) if t == current_tool else (195, 195, 195)
        pygame.draw.rect(screen, col, (x, 8, TOOL_BTN_W, 34), border_radius=4)
        pygame.draw.rect(screen, (90, 90, 90), (x, 8, TOOL_BTN_W, 34), 1, border_radius=4)
        txt = font.render(label, True, (0, 0, 0))
        screen.blit(txt, (x + 8, 19))

    # color swatches
    for i, c in enumerate(PALETTE):
        x = 320 + i * 36
        pygame.draw.rect(screen, c, (x, 10, 30, 30))
        thick  = 3 if c == current_color else 1
        border = (0, 0, 0) if c == current_color else (80, 80, 80)
        pygame.draw.rect(screen, border, (x, 10, 30, 30), thick)

    # brush size preview
    pygame.draw.circle(screen, current_color, (WIDTH - 25, 25), min(brush_size, 20))


def handle_toolbar_click(pos):
    global current_tool, current_color

    # check tool buttons
    for i, (t, _) in enumerate(TOOLS):
        x = 4 + i * (TOOL_BTN_W + 3)
        if x <= pos[0] <= x + TOOL_BTN_W and 8 <= pos[1] <= 42:
            current_tool = t
            return True

    # check color swatches
    for i, c in enumerate(PALETTE):
        x = 320 + i * 36
        if x <= pos[0] <= x + 30 and 10 <= pos[1] <= 40:
            current_color = c
            return True

    return False


def canvas_pos(pos):
    return (pos[0], pos[1] - TOOLBAR_H)


SHAPE_TOOLS = {TOOL_RECT, TOOL_CIRCLE}


def draw_shape_on(surface, tool, color, p1, p2, size):
    if tool == TOOL_RECT:
        x = min(p1[0], p2[0])
        y = min(p1[1], p2[1])
        w = abs(p2[0] - p1[0])
        h = abs(p2[1] - p1[1])
        pygame.draw.rect(surface, color, (x, y, w, h), size)

    elif tool == TOOL_CIRCLE:
        cx = (p1[0] + p2[0]) // 2
        cy = (p1[1] + p2[1]) // 2
        r  = int(math.hypot(p2[0] - p1[0], p2[1] - p1[1]) / 2)
        if r > 0:
            pygame.draw.circle(surface, color, (cx, cy), r, size)


# main loop
running = True
while running:
    clock.tick(60)

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        # scroll wheel to change brush size
        if event.type == pygame.MOUSEWHEEL:
            brush_size = max(1, min(40, brush_size + event.y))

        if event.type == pygame.MOUSEBUTTONDOWN:
            pos = event.pos
            if pos[1] < TOOLBAR_H:
                handle_toolbar_click(pos)
            else:
                drawing   = True
                start_pos = canvas_pos(pos)
                if current_tool == TOOL_PEN:
                    pygame.draw.circle(canvas, current_color, start_pos, brush_size)
                elif current_tool == TOOL_ERASER:
                    pygame.draw.circle(canvas, (255, 255, 255), start_pos, brush_size * 3)

        if event.type == pygame.MOUSEBUTTONUP:
            if drawing and event.pos[1] >= TOOLBAR_H and start_pos:
                end_pos = canvas_pos(event.pos)
                if current_tool in SHAPE_TOOLS:
                    draw_shape_on(canvas, current_tool, current_color, start_pos, end_pos, brush_size)
            drawing   = False
            start_pos = None

        if event.type == pygame.MOUSEMOTION:
            if drawing and event.pos[1] >= TOOLBAR_H:
                cur = canvas_pos(event.pos)
                if current_tool == TOOL_PEN:
                    pygame.draw.circle(canvas, current_color, cur, brush_size)
                elif current_tool == TOOL_ERASER:
                    pygame.draw.circle(canvas, (255, 255, 255), cur, brush_size * 3)

    screen.fill((255, 255, 255))
    screen.blit(canvas, (0, TOOLBAR_H))

    # live preview while dragging a shape
    if drawing and start_pos and current_tool in SHAPE_TOOLS:
        cur     = canvas_pos(pygame.mouse.get_pos())
        preview = canvas.copy()
        draw_shape_on(preview, current_tool, current_color, start_pos, cur, brush_size)
        screen.blit(preview, (0, TOOLBAR_H))

    draw_toolbar()
    pygame.display.flip()

pygame.quit()

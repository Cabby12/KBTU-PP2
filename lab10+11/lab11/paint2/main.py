import pygame
import sys
import math

pygame.init()

WIDTH, HEIGHT = 800, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Paint")
clock = pygame.time.Clock()

TOOLBAR_H = 60  # taller toolbar to fit more tools

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
TOOL_PEN      = "pen"
TOOL_RECT     = "rect"
TOOL_SQUARE   = "square"
TOOL_CIRCLE   = "circle"
TOOL_RTRI     = "rtri"    # right triangle
TOOL_ETRI     = "etri"    # equilateral triangle
TOOL_RHOMBUS  = "rhombus"
TOOL_ERASER   = "eraser"

# state
current_color = (0, 0, 0)
current_tool  = TOOL_PEN
brush_size    = 4
drawing       = False
start_pos     = None

# canvas is a separate surface — shapes are previewed on a copy then committed on mouse up
canvas = pygame.Surface((WIDTH, HEIGHT - TOOLBAR_H))
canvas.fill((255, 255, 255))

font = pygame.font.SysFont("monospace", 12)

# tools list for toolbar rendering
TOOLS = [
    (TOOL_PEN,     "Pen"),
    (TOOL_RECT,    "Rect"),
    (TOOL_SQUARE,  "Square"),
    (TOOL_CIRCLE,  "Circle"),
    (TOOL_RTRI,    "R.Tri"),
    (TOOL_ETRI,    "Eq.Tri"),
    (TOOL_RHOMBUS, "Rhombus"),
    (TOOL_ERASER,  "Eraser"),
]

TOOL_BTN_W = 70


def draw_toolbar():
    pygame.draw.rect(screen, (210, 210, 210), (0, 0, WIDTH, TOOLBAR_H))

    # draw tool buttons in one row
    for i, (t, label) in enumerate(TOOLS):
        x   = 4 + i * (TOOL_BTN_W + 3)
        col = (170, 170, 255) if t == current_tool else (195, 195, 195)
        pygame.draw.rect(screen, col, (x, 6, TOOL_BTN_W, 26), border_radius=3)
        pygame.draw.rect(screen, (90, 90, 90), (x, 6, TOOL_BTN_W, 26), 1, border_radius=3)
        txt = font.render(label, True, (0, 0, 0))
        screen.blit(txt, (x + 5, 13))

    # color swatches row below tools
    for i, c in enumerate(PALETTE):
        x = 4 + i * 34
        pygame.draw.rect(screen, c, (x, 36, 28, 18))
        border = (0, 0, 0) if c == current_color else (90, 90, 90)
        thick  = 3 if c == current_color else 1
        pygame.draw.rect(screen, border, (x, 36, 28, 18), thick)

    # current brush size preview circle
    pygame.draw.circle(screen, current_color, (WIDTH - 30, 30), min(brush_size, 20))
    sz_txt = font.render("sz:" + str(brush_size), True, (0, 0, 0))
    screen.blit(sz_txt, (WIDTH - 70, 48))


def handle_toolbar_click(pos):
    global current_tool, current_color

    # tool button row
    for i, (t, _) in enumerate(TOOLS):
        x = 4 + i * (TOOL_BTN_W + 3)
        if x <= pos[0] <= x + TOOL_BTN_W and 6 <= pos[1] <= 32:
            current_tool = t
            return True

    # color swatch row
    for i, c in enumerate(PALETTE):
        x = 4 + i * 34
        if x <= pos[0] <= x + 28 and 36 <= pos[1] <= 54:
            current_color = c
            return True

    return False


def canvas_pos(pos):
    # convert screen position to canvas position
    return (pos[0], pos[1] - TOOLBAR_H)


# --- shape drawing helpers ---

def draw_right_triangle(surface, color, p1, p2, width):
    # right angle at bottom-left of bounding box
    # p1 = drag start, p2 = drag end
    bl = (p1[0], p2[1])   # bottom-left = right angle
    pygame.draw.polygon(surface, color, [p1, p2, bl], width)


def draw_equilateral_triangle(surface, color, p1, p2, width):
    # base is from p1 to p2, third point is above the midpoint
    mx  = (p1[0] + p2[0]) / 2
    my  = (p1[1] + p2[1]) / 2
    # height of equilateral triangle = base * sqrt(3)/2
    base = math.hypot(p2[0] - p1[0], p2[1] - p1[1])
    h    = base * (math.sqrt(3) / 2)
    # perpendicular direction to the base
    dx = p2[0] - p1[0]
    dy = p2[1] - p1[1]
    length = math.hypot(dx, dy)
    if length == 0:
        return
    # unit perpendicular
    px = -dy / length
    py =  dx / length
    apex = (mx + px * h, my + py * h)
    pygame.draw.polygon(surface, color, [p1, p2, apex], width)


def draw_rhombus(surface, color, p1, p2, width):
    # rhombus centered between p1 and p2, touching all 4 sides of bounding box
    cx = (p1[0] + p2[0]) / 2
    cy = (p1[1] + p2[1]) / 2
    top    = (cx, p1[1])
    right  = (p2[0], cy)
    bottom = (cx, p2[1])
    left   = (p1[0], cy)
    pygame.draw.polygon(surface, color, [top, right, bottom, left], width)


def draw_square(surface, color, p1, p2, width):
    # force equal width and height (use the smaller dimension)
    dx = p2[0] - p1[0]
    dy = p2[1] - p1[1]
    side = min(abs(dx), abs(dy))
    # preserve the drag direction sign
    sx = int(math.copysign(side, dx))
    sy = int(math.copysign(side, dy))
    x = min(p1[0], p1[0] + sx)
    y = min(p1[1], p1[1] + sy)
    pygame.draw.rect(surface, color, (x, y, side, side), width)


def draw_shape_on(surface, tool, color, p1, p2, size):
    # dispatch to the right drawing function based on active tool
    if tool == TOOL_RECT:
        x = min(p1[0], p2[0])
        y = min(p1[1], p2[1])
        w = abs(p2[0] - p1[0])
        h = abs(p2[1] - p1[1])
        pygame.draw.rect(surface, color, (x, y, w, h), size)

    elif tool == TOOL_SQUARE:
        draw_square(surface, color, p1, p2, size)

    elif tool == TOOL_CIRCLE:
        cx = (p1[0] + p2[0]) // 2
        cy = (p1[1] + p2[1]) // 2
        r  = int(math.hypot(p2[0] - p1[0], p2[1] - p1[1]) / 2)
        if r > 0:
            pygame.draw.circle(surface, color, (cx, cy), r, size)

    elif tool == TOOL_RTRI:
        draw_right_triangle(surface, color, p1, p2, size)

    elif tool == TOOL_ETRI:
        draw_equilateral_triangle(surface, color, p1, p2, size)

    elif tool == TOOL_RHOMBUS:
        draw_rhombus(surface, color, p1, p2, size)


# these tools use drag-to-shape and need preview
SHAPE_TOOLS = {TOOL_RECT, TOOL_SQUARE, TOOL_CIRCLE, TOOL_RTRI, TOOL_ETRI, TOOL_RHOMBUS}

# main loop
running = True
while running:
    clock.tick(60)

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        # scroll wheel changes brush/outline size
        if event.type == pygame.MOUSEWHEEL:
            brush_size = max(1, min(40, brush_size + event.y))

        if event.type == pygame.MOUSEBUTTONDOWN:
            pos = event.pos
            if pos[1] < TOOLBAR_H:
                handle_toolbar_click(pos)
            else:
                drawing   = True
                start_pos = canvas_pos(pos)
                # pen and eraser start drawing immediately
                if current_tool == TOOL_PEN:
                    pygame.draw.circle(canvas, current_color, start_pos, brush_size)
                elif current_tool == TOOL_ERASER:
                    pygame.draw.circle(canvas, (255, 255, 255), start_pos, brush_size * 3)

        if event.type == pygame.MOUSEBUTTONUP:
            if drawing and event.pos[1] >= TOOLBAR_H and start_pos:
                end_pos = canvas_pos(event.pos)
                # commit shape to canvas on mouse release
                if current_tool in SHAPE_TOOLS:
                    draw_shape_on(canvas, current_tool, current_color, start_pos, end_pos, brush_size)
            drawing   = False
            start_pos = None

        if event.type == pygame.MOUSEMOTION:
            if drawing and event.pos[1] >= TOOLBAR_H:
                cur = canvas_pos(event.pos)
                # pen and eraser draw continuously as mouse moves
                if current_tool == TOOL_PEN:
                    pygame.draw.circle(canvas, current_color, cur, brush_size)
                elif current_tool == TOOL_ERASER:
                    pygame.draw.circle(canvas, (255, 255, 255), cur, brush_size * 3)

    # render
    screen.fill((255, 255, 255))
    screen.blit(canvas, (0, TOOLBAR_H))

    # show live preview for shape tools while dragging
    if drawing and start_pos and current_tool in SHAPE_TOOLS:
        cur     = canvas_pos(pygame.mouse.get_pos())
        preview = canvas.copy()
        draw_shape_on(preview, current_tool, current_color, start_pos, cur, brush_size)
        screen.blit(preview, (0, TOOLBAR_H))

    draw_toolbar()
    pygame.display.flip()

pygame.quit()

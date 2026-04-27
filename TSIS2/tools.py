import pygame
import math
from collections import deque

# all shape drawing logic lives here

def draw_line(surface, color, p1, p2, size):
    pygame.draw.line(surface, color, p1, p2, max(1, size))

def draw_rect(surface, color, p1, p2, size):
    x = min(p1[0], p2[0])
    y = min(p1[1], p2[1])
    w = abs(p2[0] - p1[0])
    h = abs(p2[1] - p1[1])
    if w > 0 and h > 0:
        pygame.draw.rect(surface, color, (x, y, w, h), max(1, size))

def draw_square(surface, color, p1, p2, size):
    dx = p2[0] - p1[0]
    dy = p2[1] - p1[1]
    side = min(abs(dx), abs(dy))
    sx = int(math.copysign(side, dx))
    sy = int(math.copysign(side, dy))
    x = min(p1[0], p1[0] + sx)
    y = min(p1[1], p1[1] + sy)
    pygame.draw.rect(surface, color, (x, y, side, side), max(1, size))

def draw_circle(surface, color, p1, p2, size):
    cx = (p1[0] + p2[0]) // 2
    cy = (p1[1] + p2[1]) // 2
    r = int(math.hypot(p2[0] - p1[0], p2[1] - p1[1]) / 2)
    if r > 0:
        pygame.draw.circle(surface, color, (cx, cy), r, max(1, size))

def draw_right_triangle(surface, color, p1, p2, size):
    bl = (p1[0], p2[1])
    pygame.draw.polygon(surface, color, [p1, p2, bl], max(1, size))

def draw_eq_triangle(surface, color, p1, p2, size):
    mx = (p1[0] + p2[0]) / 2
    my = (p1[1] + p2[1]) / 2
    base = math.hypot(p2[0] - p1[0], p2[1] - p1[1])
    h = base * (math.sqrt(3) / 2)
    dx = p2[0] - p1[0]
    dy = p2[1] - p1[1]
    length = math.hypot(dx, dy)
    if length == 0:
        return
    px = -dy / length
    py = dx / length
    apex = (mx + px * h, my + py * h)
    pygame.draw.polygon(surface, color, [p1, p2, apex], max(1, size))

def draw_rhombus(surface, color, p1, p2, size):
    cx = (p1[0] + p2[0]) / 2
    cy = (p1[1] + p2[1]) / 2
    pygame.draw.polygon(surface, color, [
        (cx, p1[1]), (p2[0], cy), (cx, p2[1]), (p1[0], cy)
    ], max(1, size))

def flood_fill(surface, pos, fill_color):
    target = surface.get_at(pos)[:3]
    if target == fill_color[:3]:
        return
    w, h = surface.get_size()
    visited = set()
    q = deque([pos])
    while q:
        x, y = q.popleft()
        if (x, y) in visited:
            continue
        if x < 0 or x >= w or y < 0 or y >= h:
            continue
        if surface.get_at((x, y))[:3] != target:
            continue
        visited.add((x, y))
        surface.set_at((x, y), fill_color)
        q.append((x+1, y))
        q.append((x-1, y))
        q.append((x, y+1))
        q.append((x, y-1))

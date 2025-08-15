import pygame

def draw_points(surface, points):
    for p in points:
        pygame.draw.circle(surface, "yellow", p, 3) 

def draw_edges(surface, triangulation, InftyPoint):
    for triangle in triangulation.faces:
        a, b, c = triangle
        if c == InftyPoint:
            continue
        else :
            for i in range(3):
                pygame.draw.line(surface, "cyan", triangle[i-1], triangle[i], 2)

def draw_Gab_edges(surface, Gab_edges):
    for edge in Gab_edges:
        a, b = edge
        pygame.draw.line(surface, "red", a, b, 3)

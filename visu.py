import pygame

def draw_points(surface, points, color):
    for p in points:
        pygame.draw.circle(surface, color, p, 3) 

def draw_edges(surface, graph, color, size):
    for edge in graph.edges:
        a, b = edge
        pygame.draw.line(surface, color, a, b, size)

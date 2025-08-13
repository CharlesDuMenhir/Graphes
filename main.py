import sys #pour fermer proprement le script
import pygame
import random


import button
from delaunay2D import *
import utils

pygame.init()

WIDTH, HEIGHT = 600, 600
FPS = 60 # pas sur d'utiliser

MENU_WIDTH = 300
MENU_LEFT = WIDTH + 10 # décalage pour le texte du menu
FONT_SIZE = 20

screen = pygame.display.set_mode((WIDTH + MENU_WIDTH, HEIGHT))
font = pygame.font.SysFont("arialblack", FONT_SIZE)
TEXT_COLOR = "white"

POINT_INF = "POINT_INF"


def draw_points(surface, points):
    for p in points:
        pygame.draw.circle(surface, "yellow", p, 3) 

def draw_edges(surface, triangulation):
    for triangle in triangulation.faces:
        a, b, c = triangle
        if c == POINT_INF:
            continue
        else :
            for i in range(3):
                pygame.draw.line(surface, "cyan", triangle[i-1], triangle[i], 2)


def draw_menu(surface, menu_buttons, pos_mouse, action):
    pygame.draw.line(screen, "grey",(WIDTH, 0),(WIDTH, HEIGHT))
    for b in menu_buttons:
        b.update(surface)
        if not action  or (action and b != menu_buttons[2]) :
            b.changeColorHover(pos_mouse, font)

def main():
    running = True
    pygame.display.set_caption("Triangulation 2D")
    clock = pygame.time.Clock()

    # Initialise les boutons du menus
    button_height = 120
    b_generate = button.Button(MENU_LEFT, button_height, 'Générer points', font)
    button_height += 40
    b_supprAll = button.Button(MENU_LEFT, button_height, 'Supprimer tous les points', font)
    button_height += 40
    b_triangulate = button.Button(MENU_LEFT, button_height, 'Trianguler', font)
    button_height += 40
    b_addPoint = button.Button(MENU_LEFT, button_height, 'Ajouter point', font)
    menu_buttons = [b_generate, b_triangulate, b_addPoint, b_supprAll]

    points = []
    n = 500 # nombre de points
    triangulation = Del_Tri(POINT_INF)
    triangulated = False
    adding = False # marqueur d'ajout en cours
    while running:
        clock.tick(FPS)
        x, y = pygame.mouse.get_pos()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            if event.type == pygame.MOUSEBUTTONDOWN:
                if x >= WIDTH:
                    adding = False
                    b_addPoint.changeColor(font, "white")

                if b_generate.checkForInput((x,y)):
                    #Supprimer l'ancienne triangulatione et genere des points
                    points = []
                    triangulation = Del_Tri(POINT_INF)
                    triangulated = False
                    # Genere n points
                    for _ in range(n):
                        x = WIDTH * random.random()
                        y = HEIGHT * random.random()
                        points.append((x,y))

                if b_supprAll.checkForInput((x,y)):
                    #Supprimer les points
                    points = []
                    triangulation = Del_Tri(POINT_INF)
                    triangulated = False                

                if b_triangulate.checkForInput((x,y)):
                    #Crée une triangulation à partir des points
                    triangulation.creates_Tri(points)
                    triangulated = True
                    
                if b_addPoint.checkForInput((x,y)):
                    adding = True
                    b_addPoint.changeColor(font, "cyan")

                if x < WIDTH and adding == True:
                    x, y = pygame.mouse.get_pos()
                    if x < WIDTH : # Si dans le jeu
                        points.append((x, y))
                        if triangulated:
                           triangulation.add_point((x, y))

                
        screen.fill((0, 0, 0)) #background
        draw_edges(screen, triangulation)
        draw_points(screen, points)
        draw_menu(screen, menu_buttons, (x, y), adding)
        pygame.display.flip()     # Affiche le rendu

    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()
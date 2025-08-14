import sys #pour fermer proprement le script
import pygame
import random

#imports locaux
from delaunay2D import *
import menu
import visu

pygame.init()

# création de la fenetre jeu + menu
FPS = 60
WIDTH, HEIGHT = 600, 600 # fenetre de jeu
MENU_WIDTH = 300 # fenetre du menu
FONT_SIZE = 15
screen = pygame.display.set_mode((WIDTH + MENU_WIDTH, HEIGHT))
font = pygame.font.SysFont("arialblack", FONT_SIZE)

#menu
option_menu = menu.Menu(screen, WIDTH, (MENU_WIDTH, HEIGHT))
t_surf = menu.Button(screen, font, "Surfaces :")
b_plan = menu.Button(screen, font, "Plan", True, True)
b_tore = menu.Button(screen, font, "Tore plat", True)
t_act = menu.Button(screen, font, "Actions :")
b_gen = menu.Button(screen, font, "Générer points", True)
b_ajout = menu.Button(screen, font, "Ajouter point", True)
b_suppr = menu.Button(screen, font, "Supprimer points", True)
t_graph = menu.Button(screen, font, "Graphes :")
b_Del = menu.Button(screen, font, "Delaunay", True, True)
b_Gab = menu.Button(screen, font, "Gabriel")
b_MST = menu.Button(screen, font, "Min Span Tree")

MENU_LEFT = WIDTH + 10 # décalage pour le texte du menu
HEIGHT_BOUTONS = 40
INTER_BOUTONS = 25

menu_surface = [t_surf, b_plan, b_tore]
for b in menu_surface:
    b.set_pos(MENU_LEFT, HEIGHT_BOUTONS)
    HEIGHT_BOUTONS += INTER_BOUTONS

HEIGHT_BOUTONS += INTER_BOUTONS
menu_action = [t_act, b_gen, b_ajout, b_suppr]
for b in menu_action:
    b.set_pos(MENU_LEFT, HEIGHT_BOUTONS)
    HEIGHT_BOUTONS += INTER_BOUTONS
    
HEIGHT_BOUTONS += INTER_BOUTONS
menu_graphe = [t_graph, b_Del, b_Gab, b_MST]
for b in menu_graphe:
    b.set_pos(MENU_LEFT, HEIGHT_BOUTONS)
    HEIGHT_BOUTONS += INTER_BOUTONS

TEXT_COLOR = "white"
TEXT_COLOR_ACTIF = "cyan"

#Pour les graphes
POINT_INF = "POINT_INF" # pour la triangulation dans le plan
H_WIDTH = WIDTH // 2
D_POINTS =[(0, 0), (H_WIDTH, 0), (0, H_WIDTH), (H_WIDTH, H_WIDTH)] #les 4 Dummy points pour le tore

def main():
    running = True
    pygame.display.set_caption("Triangulation 2D")
    clock = pygame.time.Clock()

    points = []
    n = 100 # nombre de points
    triangulation = Del_Tri(POINT_INF)
    while running:
        clock.tick(FPS)
        mouse_pos = pygame.mouse.get_pos()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            if event.type == pygame.MOUSEBUTTONDOWN:
                x, y = mouse_pos

                if x >= WIDTH:
                    b_ajout.set_inactif()

                if b_plan.under_mouse((x, y)):
                    if not b_plan.is_actif():
                        points = []
                        b_plan.set_actif()
                        b_tore.set_inactif()
                        triangulation = Del_Tri(POINT_INF)

                if b_tore.under_mouse((x, y)):
                    if not b_tore.is_actif():
                        points = []
                        b_plan.set_inactif()
                        b_tore.set_actif()
                        triangulation = Del_Tri(POINT_INF)
                        points = D_POINTS 
                        copies = utils.create_copies(points, WIDTH)
                        points.extend(copies)
                        triangulation.creates_Tri(points)

                if b_gen.under_mouse(mouse_pos):
                    #Supprimer l'ancienne triangulation et genere des points
                    #crée les graphes
                    points = []
                    triangulation = Del_Tri(POINT_INF)
                    # Genere n points
                    for _ in range(n):
                        x = WIDTH * random.random()
                        y = HEIGHT * random.random()
                        points.append((x,y))
                    if b_tore.is_actif():
                        copies = utils.create_copies(points, WIDTH)
                        points.extend(copies)
                    triangulation.creates_Tri(points)

                if b_ajout.under_mouse(mouse_pos):
                    b_ajout.set_actif()

                if x < WIDTH and b_ajout.is_actif():
                    if x < WIDTH : # Si dans le jeu
                        points.append((x, y))
                        triangulation.add_point((x, y))
                        if b_tore.is_actif():
                            copies = utils.create_copies([(x,y)], WIDTH)
                            for copie in copies:
                                triangulation.add_point(copie)
                            points.extend(copies)


                if b_suppr.under_mouse(mouse_pos):
                    #Supprimer les points
                    points = []
                    triangulation = Del_Tri(POINT_INF)
                    if b_tore.is_actif():
                        points = D_POINTS
                        triangulation.creates_Tri(points)

                if b_Del.under_mouse(mouse_pos):
                    #Affiche/masque la triangulation
                    b_Del.switch_actif()
                
        screen.fill((0, 0, 0)) #background
        if b_Del.is_actif():
            visu.draw_edges(screen, triangulation, POINT_INF)
        visu.draw_points(screen, points)
        option_menu.draw_menu_window()
        for b in menu_surface + menu_action + menu_graphe:
            b.draw_hover(mouse_pos)
            b.draw()
        
        pygame.display.flip()     # Affiche le rendu

    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()
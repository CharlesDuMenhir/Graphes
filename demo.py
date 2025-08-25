import sys #pour fermer proprement le script
import pygame
import random

#imports locaux
from graphs import *
import window

pygame.init()

# création de la fenetre jeu + menu
FPS = 60

WIDTH, HEIGHT = 700, 700 # fenetre de jeu
MENU_WIDTH = 300 # fenetre du menu
FONT_SIZE = 15
screen = pygame.display.set_mode((WIDTH + MENU_WIDTH, HEIGHT))
font = pygame.font.SysFont("Verdana", FONT_SIZE)

SCALE = window.SCALE
visu_surface = pygame.Surface((WIDTH * SCALE, HEIGHT * SCALE))  # "écran des graphes",sera rescalée, c'est pour le rendu

#menu
t_surf = window.Button(font, "Surfaces :")
b_plane = window.Button(font, " Plan ", True, True)
b_torus = window.Button(font, " Tore plat ", True)
t_act = window.Button(font, "Actions :")
b_gen = window.Button(font, " Générer points ", True)
b_n = window.Button(font, " 100   ", True)
b_ajout = window.Button(font, " Ajouter point ", True)
b_suppr = window.Button(font, " Supprimer points ", True)
t_graph = window.Button(font, "Graphes :")
b_points = window.Button(font, " Points ", True, True)
b_Del = window.Button(font, " Delaunay ", True, True)
b_Vor = window.Button(font, " Voronoï ")
b_Vor_ON_OFF = window.ON_OFF_Button(font, " OFF ", b_Vor, True)
b_Gab = window.Button(font, " Gabriel ")
b_Gab_ON_OFF = window.ON_OFF_Button(font, " OFF ", b_Gab, True)
b_RNG = window.Button(font, " RNG ")
b_RNG_ON_OFF = window.ON_OFF_Button(font, " OFF ", b_RNG, True)
b_MST = window.Button(font, " Min Span Tree")  
b_MST_ON_OFF = window.ON_OFF_Button(font, " OFF ", b_MST, True)

MENU_LEFT = WIDTH + 10 # décalage pour le texte du menu
HEIGHT_BOUTONS = 40
INTER_BOUTONS = 25

surface_buttons = [t_surf, b_plane, b_torus]
for b in surface_buttons:
    b.set_pos(MENU_LEFT, HEIGHT_BOUTONS)
    HEIGHT_BOUTONS += INTER_BOUTONS

HEIGHT_BOUTONS += INTER_BOUTONS
action_buttons = [t_act, b_gen, b_ajout, b_suppr]
for b in action_buttons:
    b.set_pos(MENU_LEFT, HEIGHT_BOUTONS)
    HEIGHT_BOUTONS += INTER_BOUTONS

b_n.set_pos(b_gen.rect.x + 200, b_gen.rect.y)
    
HEIGHT_BOUTONS += INTER_BOUTONS
graph_buttons = [t_graph, b_points, b_Del, b_Vor, b_Gab, b_RNG, b_MST]
for b in graph_buttons:
    b.set_pos(MENU_LEFT, HEIGHT_BOUTONS)
    HEIGHT_BOUTONS += INTER_BOUTONS

ON_OFF_buttons = [b_Gab_ON_OFF, b_Vor_ON_OFF, b_RNG_ON_OFF, b_MST_ON_OFF]
for b in ON_OFF_buttons:
    b.set_pos(b.cible.rect.x + 150, b.cible.rect.y)

all_buttons = surface_buttons + action_buttons + [b_n] + graph_buttons + ON_OFF_buttons

# Pour la fenetre de dessin
H_WIDTH = WIDTH // 2 # pour le tore
P_COLOR = (50, 45, 100)
DEL_COLOR = "black"
VOR_COLOR = "magenta"
GAB_COLOR = "red"
RNG_COLOR = "blue"
MST_COLOR = "green"
GRAPH_BACKGROUND = "white"

def main():
    running = True
    pygame.display.set_caption("Triangulation 2D")
    clock = pygame.time.Clock()

    points = []
    n = 300 # nombre de points à générer par defaut
    input_text = " " + str(n)
    b_n.change_text_to(font, input_text)
    DT = Delaunay_Triangulation()
    VD = Voronoi_Diagram()
    GG = Gabriel_Graph()
    RNG = Rel_Neighbor_Graph()
    MST = Minimal_Spanning_Tree()
    b_Vor_ON_OFF.graph = VD
    b_Gab_ON_OFF.graph = GG
    b_RNG_ON_OFF.graph = RNG
    b_MST_ON_OFF.graph = MST
    graphs = (DT, VD, GG, RNG, MST)
    while running:
        clock.tick(FPS)
        mouse_pos = pygame.mouse.get_pos()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            elif event.type == pygame.MOUSEBUTTONDOWN:
                x, y = mouse_pos

                if x >= WIDTH:
                    b_ajout.set_inactive()

                if b_plane.rect.collidepoint((x, y)):
                    if not b_plane.is_active:
                        b_plane.set_active()
                        b_torus.set_inactive()
                        points = []
                        for g in graphs:
                            g.reset()
                  

                if b_torus.rect.collidepoint((x, y)):
                    if not b_torus.is_active:
                        b_plane.set_inactive()
                        b_torus.set_active()
                        copies = window.create_copies(points, WIDTH)
                        points.extend(copies)
                        DT.build(points)
                        for b in ON_OFF_buttons:
                            if b.is_ON:
                                b.graph.extract_from_Del(DT)

                if b_gen.rect.collidepoint(mouse_pos):
                    # Supprimer l'ancienne triangulation et genere des points
                    # crée les graphes
                    points = []                
                    # Genere n points
                    for _ in range(n):
                        x = WIDTH * random.random()
                        y = HEIGHT * random.random()
                        points.append((x,y))
                    if b_torus.is_active:  # on considère qu'il y a suffisament de points pour éviter les dummy points
                        copies = window.create_copies(points, WIDTH)
                        points.extend(copies)
                    # et crée les graphes
                    DT.build(points)
                    for b in ON_OFF_buttons:
                        if b.cible.is_ON:
                            b.graph.extract_from_Del(DT)

                if b_n.rect.collidepoint(mouse_pos):
                    b_n.set_active()
                    input_text = " "

                if b_ajout.rect.collidepoint(mouse_pos):
                    b_ajout.set_active()

                if x < WIDTH and b_ajout.is_active:  # gère l'ajout de point dans la fenetre
                    if x < WIDTH : # Si dans le jeu
                        points.append((x, y))
                        DT.insert_point((x,y))
                        if b_torus.is_active:
                            copies = window.create_copies([(x,y)], WIDTH)
                            for copie in copies:
                                DT.insert_point(copie)
                            points.extend(copies) 
                        for b in ON_OFF_buttons:
                            if b.cible.is_ON:
                                b.graph.extract_from_Del(DT)  # ca recalcule integralement les sous graphs! => possibilité de les désactiver

                if b_suppr.rect.collidepoint(mouse_pos): # Supprimer les points
                    points = []
                    for g in graphs:
                        g.reset()

                for b in graph_buttons:     # Affiche/masque les graphs actifs/inactifs
                    if b.rect.collidepoint(mouse_pos) and b.is_ON:
                        b.switch_active()
                
                for b in ON_OFF_buttons:
                    if b.rect.collidepoint(mouse_pos):
                        if b.cible.is_ON:
                            b.change_text_to(font," OFF ")
                            b.cible.set_inactive()
                            b.graph.reset
                        else:
                            b.change_text_to(font," ON ")
                            b.graph.extract_from_Del(DT)   
                        b.cible.switch_ON_OFF()

            elif event.type == pygame.KEYDOWN:
                if b_n.is_active:                       # selection du nombre de points
                    if event.key == pygame.K_RETURN:
                        print("Nombre entré :", input_text)
                        try:
                            new_n = int(input_text)
                            max_n = 5000
                            if 0 < new_n and new_n <= max_n:
                                n = new_n
                            else:
                                print("Entrée invalide")
                                print("max = ", max_n)
                        except ValueError:
                            print("Entrée invalide")    
                        input_text = str(n)
                        b_n.set_inactive()
                    elif event.key == pygame.K_BACKSPACE:
                        input_text = input_text[:-1]
                    else:
                        input_text += event.unicode
                    b_n.change_text_to(font," " + input_text)

        
        screen.fill(window.DARK_BLUE)
        visu_surface.fill(GRAPH_BACKGROUND)
        if b_Del.is_active:    
                window.draw_edges(visu_surface, DT, DEL_COLOR, 2)
        if b_Vor.is_active:    
                window.draw_edges(visu_surface, VD, VOR_COLOR, 3, WIDTH)
        if b_Gab.is_active:
            window.draw_edges(visu_surface, GG, GAB_COLOR, 3)  
        if b_RNG.is_active:
            window.draw_edges(visu_surface, RNG, RNG_COLOR, 3)
        if b_MST.is_active:
            window.draw_edges(visu_surface, MST, MST_COLOR, 3)
        if b_points.is_active:
            window.draw_points(visu_surface, points, P_COLOR)
        scaled_surface = pygame.transform.smoothscale(visu_surface, (WIDTH, HEIGHT))
        screen.blit(scaled_surface, (0, 0))
        window.draw_menu_line(screen, WIDTH, (MENU_WIDTH, HEIGHT))
        for b in all_buttons:
            window.draw_button(screen, b, mouse_pos)
        pygame.display.flip()     # Affiche le rendu

    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()
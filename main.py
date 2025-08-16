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
b_plan = menu.Button(screen, font, " Plan ", True, True)
b_tore = menu.Button(screen, font, " Tore plat ", True)
t_act = menu.Button(screen, font, "Actions :")
b_gen = menu.Button(screen, font, " Générer points ", True)
b_n = menu.Button(screen, font, "   100 ", True)
b_ajout = menu.Button(screen, font, " Ajouter point ", True)
b_suppr = menu.Button(screen, font, " Supprimer points ", True)
t_graph = menu.Button(screen, font, "Graphes :")
b_Del = menu.Button(screen, font, " Delaunay ", True, True)
b_Gab = menu.Button(screen, font, " Gabriel ", False)
b_OnOff = menu.Button(screen, font, " OFF ", True)
# plus tard :
#b_MST = menu.Button(screen, font, "Min Span Tree")  

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

b_n.set_pos(b_gen.rect.x + 150, b_gen.rect.y)
    
HEIGHT_BOUTONS += INTER_BOUTONS
menu_graphe = [t_graph, b_Del, b_Gab]
for b in menu_graphe:
    b.set_pos(MENU_LEFT, HEIGHT_BOUTONS)
    HEIGHT_BOUTONS += INTER_BOUTONS

b_OnOff.set_pos(b_Gab.rect.x + 100, b_Gab.rect.y)


#Pour les graphes
POINT_INF = "POINT_INF" # pour la triangulation dans le plan
H_WIDTH = WIDTH // 2
D_POINTS =[(0, 0), (H_WIDTH, 0), (0, H_WIDTH), (H_WIDTH, H_WIDTH)] #les 4 Dummy points pour le tore

def main():
    running = True
    pygame.display.set_caption("Triangulation 2D")
    clock = pygame.time.Clock()

    points = []
    n = 100 # nombre de points à générer par defaut
    input_text = ''
    triangulation = Del_Tri(POINT_INF)
    gabriel = Gabriel(POINT_INF)
    while running:
        clock.tick(FPS)
        mouse_pos = pygame.mouse.get_pos()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            elif event.type == pygame.MOUSEBUTTONDOWN:
                x, y = mouse_pos

                if x >= WIDTH:
                    b_ajout.set_inactif()

                if b_plan.rect.collidepoint((x, y)):
                    if not b_plan.is_actif():
                        points = []
                        b_plan.set_actif()
                        b_tore.set_inactif()
                        triangulation = Del_Tri(POINT_INF)
                        gabriel = Gabriel(POINT_INF)

                if b_tore.rect.collidepoint((x, y)):
                    if not b_tore.is_actif():
                        points = []
                        b_plan.set_inactif()
                        b_tore.set_actif()
                        triangulation = Del_Tri(POINT_INF)
                        gabriel = Gabriel(POINT_INF)
                        points.extend(D_POINTS) 
                        copies = utils.create_copies(points, WIDTH)
                        points.extend(copies)
                        triangulation.creates_Tri(points)
                        if b_Gab.is_activable():
                            gabriel.extract_Gab_from_Del(points, triangulation.faces)

                if b_gen.rect.collidepoint(mouse_pos):
                    # Supprimer l'ancienne triangulation et genere des points
                    # crée les graphes
                    points = []
                    triangulation = Del_Tri(POINT_INF)
                    gabriel = Gabriel(POINT_INF)
                    
                    # Genere n points
                    for _ in range(n):
                        x = WIDTH * random.random()
                        y = HEIGHT * random.random()
                        points.append((x,y))
                    if b_tore.is_actif():  # on considère qu'il y a suffisament de points pour éviter les dummy points
                        copies = utils.create_copies(points, WIDTH)
                        points.extend(copies)
                    triangulation.creates_Tri(points)
                    if b_Gab.is_activable():
                        gabriel.extract_Gab_from_Del(points, triangulation.faces)

                if b_n.rect.collidepoint(mouse_pos):
                    b_n.set_actif()
                    input_text = ''

                if b_ajout.rect.collidepoint(mouse_pos):
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
                    gabriel = Gabriel(POINT_INF) #recalcule tout le graph de Delaunay à chaque fois
                    if b_Gab.is_activable():
                        gabriel.extract_Gab_from_Del(points, triangulation.faces)

                if b_suppr.rect.collidepoint(mouse_pos):
                    #Supprimer les points
                    points = []
                    triangulation = Del_Tri(POINT_INF)
                    gabriel = Gabriel(POINT_INF)
                    if b_tore.is_actif():
                        points.extend(D_POINTS)
                        copies = utils.create_copies(points, WIDTH)
                        points.extend(copies)
                        triangulation.creates_Tri(points)
                        if b_Gab.is_activable():
                            gabriel.extract_Gab_from_Del(points, triangulation.faces)

                if b_Del.rect.collidepoint(mouse_pos):
                    #Affiche/masque la triangulation
                    b_Del.switch_actif()

                if b_Gab.rect.collidepoint(mouse_pos):
                    #Affiche/masque la triangulation
                    if b_OnOff.text_input == " ON ":
                        b_Gab.switch_actif()
                
                if b_OnOff.rect.collidepoint(mouse_pos):
                    # desactive gabriel
                    b_Gab.switch_activable()
                    if b_OnOff.text_input == " OFF ":
                        b_OnOff.change_text_to(font," ON ")
                        gabriel.extract_Gab_from_Del(points, triangulation.faces)

                    else:
                        b_OnOff.change_text_to(font," OFF ")
                        b_Gab.set_inactif()
                        gabriel = Gabriel(POINT_INF)

            elif event.type == pygame.KEYDOWN:
                if b_n.is_actif():
                    if event.key == pygame.K_RETURN:
                        print("Nombre entré :", input_text)
                        # Tu peux convertir en int ici si besoin
                        try:
                            new_n = int(input_text)
                            max_n = 1000
                            if 0 < new_n and new_n <= 1000:
                                n = new_n
                            else:
                                print("max = ", max_n)
                        except ValueError:
                            print("Entrée invalide")    
                        input_text = str(n)
                        b_n.set_inactif()
                    elif event.key == pygame.K_BACKSPACE:
                        input_text = input_text[:-1]
                    else:
                        input_text += event.unicode
                    b_n.change_text_to(font," " + input_text)


                
        screen.fill((0, 0, 0)) #background
        if b_Del.is_actif():
            visu.draw_edges(screen, triangulation, POINT_INF)
        if b_Gab.is_actif():    
            visu.draw_Gab_edges(screen, gabriel.Gab_edges)
        visu.draw_points(screen, points)
        option_menu.draw_menu_window()
        for b in menu_surface + menu_action + [b_n] + menu_graphe + [b_OnOff]:
            b.draw(mouse_pos)
 
        pygame.display.flip()     # Affiche le rendu

    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()
"""
Module d'affichage graphique pour la visualisation des graphes et de la triangulation.
Utilise pygame pour dessiner points, arêtes, boutons et menus.
"""

import pygame
from typing import Tuple, List, Any

#------------------------------------Définitions des couleurs

WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
CYAN = (0, 255, 255)
GRAY = (200, 200, 200)
BLUE_GRAY = (70, 73, 105)
DARK_BLUE = (3, 6, 33)

TEXT_COLOR = WHITE
TEXT_COLOR_ACTIF = CYAN
HOVER_COLOR = BLUE_GRAY

#--------------------------Classes de bouton--------------------------------

class Button:
    """Bouton interactif pour l'interface graphique pygame."""
    #Source : BaralTech
    def __init__(self, font: Any, text_input: str, OFF: bool = False, active: bool = False):
        self.font = font
        self.text_input = text_input
        self.text_surf = font.render(self.text_input, True, TEXT_COLOR)
        self.rect = self.text_surf.get_rect(bottomleft=(0, 0))
        self.is_ON = OFF  # permet d'activer ou non certain bouton (desactive par défaut les titres et les boutons en off)
        self.active = active # flag les boutons actifs 

    def switch_ON_OFF(self) -> None:
        self.is_ON = not self.is_ON
        
    def set_active(self) -> None:
        self.active = True

    def set_inactive(self) -> None:
        self.active = False

    def switch_active(self) -> None:
        self.active = not self.active

    @property
    def is_active(self) -> bool:
        return self.active

    def set_pos(self, x_pos: int, y_pos: int) -> None:  
        self.rect.x = x_pos
        self.rect.y = y_pos

    def change_text_to(self, font: Any, new_text: str) -> None:
        self.text_input = new_text
        self.text_surf = font.render(self.text_input, True, TEXT_COLOR)

class ON_OFF_Button(Button):
    """Bouton à deux états (ON/OFF) pour activer ou désactiver une fonctionnalité."""
    def __init__(self, font: Any, text_input: str, cible: Any, graph: Any = None, OFF: bool = False, active: bool = False):
        super().__init__(font, text_input, OFF, active)
        self.cible = cible
        self.graph = graph


#---------------------------------Fonctions d'affichage------------------------------

def draw_button(surface: pygame.Surface, b: "Button", mouse_pos: Tuple[int, int]) -> None:
    """Affiche un bouton sur la surface pygame, en tenant compte de la position de la souris."""
    color = TEXT_COLOR_ACTIF if b.is_active else TEXT_COLOR
    b.text_surf = b.font.render(b.text_input, True, color)
    if b.is_ON and b.rect.collidepoint(mouse_pos):
        pygame.draw.rect(surface, HOVER_COLOR, b.rect)
    surface.blit(b.text_surf, b.rect)

# Pour représenter les graphes

def draw_menu_line(surface: pygame.Surface, x_pos: int, size: int) -> None:
    """Dessine une ligne de séparation de menu sur la surface pygame."""
    w, h = size
    pygame.draw.line(surface, GRAY, (x_pos, 0), (x_pos, h)) # ligne grise verticale

def draw_points(surface: Any, points: List[Tuple[float, float]], color, size , scale: int) -> None:
    """Dessine une liste de points sur la surface pygame."""
    for p in points:
        x, y = p
        pygame.draw.circle(surface, color, (x*scale, y*scale), size*scale) 

def draw_edges(surface: pygame.Surface, graph, color, size: int, scale: int, max: int = 0) -> None:
    """Dessine les arêtes d'un graphe sur la surface pygame."""
    for edge in graph.edges:
        if edge.is_infinite:
            edge = edge.desinfinite(max)
        a, b = edge.vertices
        ax, ay = a.coord
        bx, by = b.coord
        pygame.draw.line(surface, color, (ax*scale, ay*scale), (bx*scale, by*scale), size*scale)


#----------------------Pour représenter le tore plat------------

def create_copies(points: List[Tuple[float, float]], width: int) -> List[Tuple[float, float]]:
    """Crée des copies translatées des points pour simuler un tore plat."""
    # crée 3 copies de la liste de points autour de l'écran
    # w est la largueur de l'écran
    copies = []
    h_width = width // 2
    for p in points: # faire une fonction
        px, py = p
        if px < h_width and py < h_width:
            copies.append((px + width, py))
            copies.append((px, py + width))
            copies.append((px + width, py + width))
        if px < h_width and py >= h_width:
            copies.append((px + width, py))
            copies.append((px, py - width))
            copies.append((px + width, py - width))
        if px >= h_width and py < h_width:
            copies.append((px - width, py))
            copies.append((px, py + width))
            copies.append((px - width, py + width))
        if px >= h_width and py >= h_width:
            copies.append((px - width, py))
            copies.append((px, py - width))
            copies.append((px - width, py - width))
    return(copies)

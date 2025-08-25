import pygame
import geom # pour différencier les Edges, des Ray

WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
CYAN = (0, 255, 255)
GRAY = (200, 200, 200)
BLUE_GRAY = (70, 73, 105)
DARK_BLUE = (3, 6, 33)

TEXT_COLOR = WHITE
TEXT_COLOR_ACTIF = CYAN
HOVER_COLOR = BLUE_GRAY

        
class Button:
    #Source : BaralTech
    def __init__(self, font, text_input, OFF = False, active = False):
        self.font = font
        self.text_input = text_input
        self.text_surf = font.render(self.text_input, True, TEXT_COLOR)
        self.rect = self.text_surf.get_rect(bottomleft=(0, 0))
        self.is_ON = OFF  # permet d'activer ou non certain bouton (desactive par défaut les titres et les boutons en off)
        self.active = active # flag les boutons actifs 

    def switch_ON_OFF(self):
        self.is_ON = not self.is_ON
        
    def set_active(self):
        self.active = True

    def set_inactive(self):
        self.active = False

    def switch_active(self):
        self.active = not self.active

    @property
    def is_active(self):
        return self.active

    def set_pos(self, x_pos, y_pos):  
        self.rect.x = x_pos
        self.rect.y = y_pos

    def change_text_to(self, font, new_text):
        self.text_input = new_text
        self.font.render(self.text_input, True, TEXT_COLOR)

class ON_OFF_Button(Button):
    def __init__(self, font, text_input, cible, graph = None, OFF = False, active = False):
        super().__init__(font, text_input, OFF = False, active = False)
        self.cible = cible
        self.graph = graph


def draw_button(surface, b, mouse_pos):
    color = TEXT_COLOR_ACTIF if b.is_active else TEXT_COLOR
    b.text_surf = b.font.render(b.text_input, True, color)
    if b.is_ON and b.rect.collidepoint(mouse_pos):
        pygame.draw.rect(surface, HOVER_COLOR, b.rect)
    surface.blit(b.text_surf, b.rect)

# Pour représenter les graphes

def draw_menu_line(surface, x_pos, size):
    w, h = size
    pygame.draw.line(surface, GRAY, (x_pos, 0), (x_pos, h)) # ligne grise verticale

SCALE = 3  # utilisé pour améliorer le rendu
def draw_points(surface, points, color):
    for p in points:
        x, y = p
        pygame.draw.circle(surface, color, (x*SCALE, y*SCALE), 3*SCALE) 


def draw_edges(surface, graph, color, size, max = 0):
    for edge in graph.edges:
        if isinstance(edge, geom.Ray):
            a = edge.vertex
            b = edge.get_point(max) # pour qu'il sorte de l'écran, mais à distance cohérente
        else :
            a, b = edge.points
            if a == geom.INF_P or b == geom.INF_P: # en pratique c'st inutile de tester les 2
                continue 
        ax, ay = a
        bx, by = b
        pygame.draw.line(surface, color, (ax*SCALE, ay*SCALE), (bx*SCALE, by*SCALE), size*SCALE)


# Pour représenter le tore plat

def create_copies(points, width):
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

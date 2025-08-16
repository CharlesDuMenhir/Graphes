import pygame


WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GRAY = (200, 200, 200)
DARK_BLUE = (31, 33, 54)

TEXT_COLOR = "white"
TEXT_COLOR_ACTIF = "cyan"

class Menu:
    def __init__(self, screen, x_pos, size):
        self.screen = screen
        self.x_pos = x_pos # pos horizontale de menu
        self.size = size
    
    def draw_menu_window(self):
        x = self.x_pos
        w, h = self.size
        pygame.draw.rect(self.screen, DARK_BLUE, (x, 0, w, h)) # fond noir du menu
        pygame.draw.line(self.screen, "grey",(x, 0), (x, h)) # ligne grise verticale
        
class Button:
    #Source : BaralTech
    def __init__(self, screen, font, text_input, activable = False, actif = False):
        self.screen = screen
        self.font = font
        self.text_input = text_input
        self.text_surf = font.render(self.text_input, True, TEXT_COLOR)
        self.rect = self.text_surf.get_rect(bottomleft=(0, 0))
        self.activable = activable  # permet d'activer ou non certain bouton (desactive les titres et les boutons en off)
        self.actif = actif # flag les boutons actifs 

    def switch_activable(self):
        self.activable = not self.activable

    def is_activable(self):
        return self.activable
        
    def set_actif(self):
        self.actif = True

    def set_inactif(self):
        self.actif = False

    def switch_actif(self):
        self.actif = not self.actif

    def is_actif(self):
        return self.actif

    def set_pos(self, x_pos, y_pos):  
        self.rect.x = x_pos
        self.rect.y = y_pos

    def change_text_to(self, font, new_text):
        self.text_input = new_text
        self.font.render(self.text_input, True, TEXT_COLOR)

    def draw(self, mouse_pos):
        color = TEXT_COLOR_ACTIF if self.is_actif() else TEXT_COLOR
        self.text_surf = self.font.render(self.text_input, True, color)
        if self.activable and self.rect.collidepoint(mouse_pos):
            pygame.draw.rect(self.screen, (60, 60, 60), self.rect)
        self.screen.blit(self.text_surf, self.rect)

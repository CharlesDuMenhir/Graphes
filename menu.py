import pygame

WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
CYAN = (0, 255, 255)
GRAY = (200, 200, 200)
BLUE_GRAY = (70, 73, 105)
DARK_BLUE = (3, 6, 33)

TEXT_COLOR = WHITE
TEXT_COLOR_ACTIF = CYAN
HOVER_COLOR = BLUE_GRAY

class Menu:
    def __init__(self, screen, x_pos, size):
        self.screen = screen
        self.x_pos = x_pos # pos horizontale de menu
        self.size = size
    
    def draw_menu_window(self):
        x = self.x_pos
        w, h = self.size
        pygame.draw.rect(self.screen, DARK_BLUE, (x, 0, w, h)) # fond noir du menu
        pygame.draw.line(self.screen, GRAY, (x, 0), (x, h)) # ligne grise verticale
        
class Button:
    #Source : BaralTech
    def __init__(self, screen, font, text_input, activable = False, active = False):
        self.screen = screen
        self.font = font
        self.text_input = text_input
        self.text_surf = font.render(self.text_input, True, TEXT_COLOR)
        self.rect = self.text_surf.get_rect(bottomleft=(0, 0))
        self.activable = activable  # permet d'activer ou non certain bouton (desactive les titres et les boutons en off)
        self.active = active # flag les boutons actifs 

    def switch_activable(self):
        self.activable = not self.activable

    def is_activable(self):
        return self.activable
        
    def set_active(self):
        self.active = True

    def set_inactive(self):
        self.active = False

    def switch_active(self):
        self.active = not self.active

    def is_active(self):
        return self.active

    def set_pos(self, x_pos, y_pos):  
        self.rect.x = x_pos
        self.rect.y = y_pos

    def change_text_to(self, font, new_text):
        self.text_input = new_text
        self.font.render(self.text_input, True, TEXT_COLOR)

    def draw(self, mouse_pos):
        color = TEXT_COLOR_ACTIF if self.is_active() else TEXT_COLOR
        self.text_surf = self.font.render(self.text_input, True, color)
        if self.activable and self.rect.collidepoint(mouse_pos):
            pygame.draw.rect(self.screen, HOVER_COLOR, self.rect)
        self.screen.blit(self.text_surf, self.rect)

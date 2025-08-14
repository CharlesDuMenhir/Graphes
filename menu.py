import pygame

class Menu():
    def __init__(self, screen, x_pos, size):
        self.screen = screen
        self.x_pos = x_pos # pos horizontale de menu
        self.size = size
    
    def draw_menu_window(self):
        x = self.x_pos
        w, h = self.size
        pygame.draw.rect(self.screen, "black", (x, 0, w, h)) # fond noir du menu
        pygame.draw.line(self.screen, "grey",(x, 0), (x, h)) # ligne grise verticale
        
class Button():
    #Source : BaralTech
    def __init__(self, screen, font, text_input, activable = False, actif = False):
        self.screen = screen
        self.font = font
        self.text_input = text_input
        self.text = font.render(self.text_input, True, "white")
        self.rect = self.text.get_rect(bottomleft=(0, 0))
        self.activable = activable
        self.actif = actif

    def set_activable(self):
        self.activable = True
        
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

    def draw(self):
        if self.is_actif():
            self.text = self.font.render(self.text_input, True, "cyan")
        else:
            self.text = self.font.render(self.text_input, True, "white")
        self.screen.blit(self.text, self.rect)
    
    def draw_hover(self, pos_mouse):
        if self.activable and self.under_mouse(pos_mouse):
            pygame.draw.rect(self.screen, (60, 60, 60), self.rect)

    def under_mouse(self, pos_mouse):
        x, y = pos_mouse
        is_under_mouse = x in range(self.rect.left, self.rect.right) and y in range(self.rect.top, self.rect.bottom)
        return is_under_mouse



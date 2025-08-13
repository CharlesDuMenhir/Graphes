#Source : BaralTech

class Button():
	def __init__(self, x_pos, y_pos, text_input, font):
		self.x_pos = x_pos
		self.y_pos = y_pos
		self.text_input = text_input
		self.text = font.render(self.text_input, True, "grey")
		self.rect = self.text.get_rect(bottomleft=(self.x_pos, self.y_pos))

	def update(self,screen):
		screen.blit(self.text, self.rect) #affiche text dans rect
                
	def checkForInput(self, position):
		inRect = position[0] in range(self.rect.left, self.rect.right) and position[1] in range(self.rect.top, self.rect.bottom)
		return inRect
	
	def changeColor(self, font, color):
		self.text = font.render(self.text_input, True, color)

	def changeColorHover(self, position, font):
		if position[0] in range(self.rect.left, self.rect.right) and position[1] in range(self.rect.top, self.rect.bottom):
			self.text = font.render(self.text_input, True, "cyan")
		else:
			self.text = font.render(self.text_input, True, "white")

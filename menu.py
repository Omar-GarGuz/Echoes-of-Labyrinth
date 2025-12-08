import pygame
from settings import *

class Button:
    def __init__(self, x, y, width, height, text, action):
        self.rect = pygame.Rect(x, y, width, height)
        self.text = text
        self.action = action
        self.hovered = False
        
        # Colors
        self.bg_color = GRAY
        self.hover_color = (150, 150, 150)
        self.text_color = WHITE
        
        # Font
        self.font = pygame.font.Font(None, 36)
        
    def update(self, mouse_pos):
        self.hovered = self.rect.collidepoint(mouse_pos)
        
    def draw(self, screen):
        # Draw button background
        color = self.hover_color if self.hovered else self.bg_color
        pygame.draw.rect(screen, color, self.rect)
        pygame.draw.rect(screen, self.text_color, self.rect, 2)
        
        # Draw button text
        text_surf = self.font.render(self.text, True, self.text_color)
        text_rect = text_surf.get_rect(center=self.rect.center)
        screen.blit(text_surf, text_rect)
        
class Menu:
    def __init__(self, game):
        self.game = game
        
        # Create buttons
        button_width = 200
        button_height = 60
        button_x = WIDTH // 2 - button_width // 2
        
        self.buttons = [
            Button(button_x, 300, button_width, button_height, "Start Game", self.start_game),
            Button(button_x, 380, button_width, button_height, "Controls", self.show_controls),
            Button(button_x, 460, button_width, button_height, "Quit", self.quit_game)
        ]
        
        # Title text
        self.title_font = pygame.font.Font(None, 72)
        self.title_text = self.title_font.render("Echoes of the Labyrinth", True, WHITE)
        self.title_rect = self.title_text.get_rect(center=(WIDTH // 2, 150))
        
        # Controls screen
        self.showing_controls = False
        self.controls_font = pygame.font.Font(None, 32)
        self.controls_text = [
            "Controls:",
            "Arrow Keys / WASD - Move",
            "Space - Jump",
            "E - Interact with objects",
            "Esc - Pause game",
            "",
            "Press any key to return"
        ]
        
    def handle_event(self, event):
        if self.showing_controls:
            if event.type == pygame.KEYDOWN:
                self.showing_controls = False
        else:
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                mouse_pos = pygame.mouse.get_pos()
                for button in self.buttons:
                    if button.rect.collidepoint(mouse_pos):
                        button.action()
                        break
        
    def update(self):
        if not self.showing_controls:
            mouse_pos = pygame.mouse.get_pos()
            for button in self.buttons:
                button.update(mouse_pos)
        
    def draw(self):
        # Draw menu background
        self.game.screen.fill(BG_COLOR)
        
        if self.showing_controls:
            self.draw_controls()
        else:
            # Draw title
            self.game.screen.blit(self.title_text, self.title_rect)
            
            # Draw buttons
            for button in self.buttons:
                button.draw(self.game.screen)
    
    def draw_controls(self):
        # Draw controls text
        for i, line in enumerate(self.controls_text):
            text_surf = self.controls_font.render(line, True, WHITE)
            text_rect = text_surf.get_rect(center=(WIDTH // 2, 150 + i * 40))
            self.game.screen.blit(text_surf, text_rect)
    
    def start_game(self):
        self.game.start_level(1)
    
    def show_controls(self):
        self.showing_controls = True
    
    def quit_game(self):
        pygame.quit()
        import sys
        sys.exit()
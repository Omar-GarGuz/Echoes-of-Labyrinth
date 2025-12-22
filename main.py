import pygame
import sys
import os
from settings import *
from player import Player
from level import Level
from ui import UI
from menu import Menu

class Game:
    def __init__(self):
        # Initialize pygame
        pygame.init()
        pygame.mixer.init()
        
        # Set up display
        self.screen = pygame.display.set_mode((WIDTH, HEIGHT))
        pygame.display.set_caption("Echoes of the Labyrinth")
        
        # Set up clock
        self.clock = pygame.time.Clock()
        
        # Game states
        self.state = "menu"  # menu, playing, paused, game_over
        
        # Sound settings (MOVE THIS BEFORE load_assets)
        self.sound_volume = 0.7
        self.music_volume = 0.5
        
        # Load assets
        self.load_assets()
        
        # Create instances
        self.menu = Menu(self)
        self.ui = UI(self)
        self.level = None
        self.player = None
        
        # Pause menu buttons
        self.pause_buttons = []
        
        # Set music volume after loading
        pygame.mixer.music.set_volume(self.music_volume)
        
    def load_assets(self):
        # Load sounds
        self.sounds = {
            'jump': pygame.mixer.Sound('assets/sounds/jump.wav'),
            'collect': pygame.mixer.Sound('assets/sounds/collect.wav'),
            'door_open': pygame.mixer.Sound('assets/sounds/door_open.wav'),
            'memory_fade': pygame.mixer.Sound('assets/sounds/memory_fade.wav'),
            'switch': pygame.mixer.Sound('assets/sounds/switch.wav')
        }
        
        for sound in self.sounds.values():
            sound.set_volume(self.sound_volume)
        
        # Load music
        self.music = {
            'menu': 'assets/music/menu_theme.mp3',
            'level1': 'assets/music/level1.mp3',
            'level2': 'assets/music/level2.mp3',
            'level3': 'assets/music/level3.mp3'
        }
    
    def start_level(self, level_number):
        self.level = Level(self, level_number)
        self.player = Player(self, self.level.player_start_pos)
        self.state = "playing"
        
        # Play level music
        pygame.mixer.music.load(self.music[f'level{level_number}'])
        pygame.mixer.music.play(-1)
    
    def pause_game(self):
        if self.state == "playing":
            self.state = "paused"
            pygame.mixer.music.pause()
        elif self.state == "paused":
            self.state = "playing"
            pygame.mixer.music.unpause()
    
    def return_to_menu_from_pause(self):
        """Return to main menu from pause screen"""
        self.level = None
        self.player = None
        self.state = "menu"
        self.menu.current_screen = "main"  # Reset menu to main screen
        try:
            pygame.mixer.music.load(self.music['menu'])
            pygame.mixer.music.play(-1)
        except Exception:
            pass
    
    def update(self):
        if self.state == "playing":
            self.player.update()
            self.level.update(self.player)
            self.ui.update()
    
    def draw(self):
        self.screen.fill(BG_COLOR)
        
        if self.state == "menu":
            self.menu.draw()
        elif self.state == "playing" or self.state == "paused":
            self.level.draw(self.screen)
            self.player.draw(self.screen)
            self.ui.draw()
            
            if self.state == "paused":
                # Draw pause overlay
                pause_surf = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
                pause_surf.fill((0, 0, 0, 128))
                self.screen.blit(pause_surf, (0, 0))
                
                # Draw pause text
                font = pygame.font.Font(None, 72)
                text = font.render("PAUSED", True, WHITE)
                text_rect = text.get_rect(center=(WIDTH//2, HEIGHT//2 - 100))
                self.screen.blit(text, text_rect)

                # Button dimensions
                btn_w, btn_h = 220, 56
                btn_spacing = 20
                center_x = WIDTH // 2
                start_y = HEIGHT // 2 - 20

                # Create buttons
                buttons = [
                    {"text": "Resume", "y_offset": 0, "action": "resume"},
                    {"text": "Restart Level", "y_offset": btn_h + btn_spacing, "action": "restart"},
                    {"text": "Main Menu", "y_offset": (btn_h + btn_spacing) * 2, "action": "menu"}
                ]

                # Clear and rebuild button list
                self.pause_buttons = []
                mouse_pos = pygame.mouse.get_pos()

                for btn in buttons:
                    btn_x = center_x - btn_w // 2
                    btn_y = start_y + btn["y_offset"]
                    btn_rect = pygame.Rect(btn_x, btn_y, btn_w, btn_h)
                    
                    # Store rect with action
                    self.pause_buttons.append({"rect": btn_rect, "action": btn["action"]})

                    # Check hover
                    is_hover = btn_rect.collidepoint(mouse_pos)
                    
                    # Draw button
                    bg_color = (220, 220, 220) if is_hover else (200, 200, 200)
                    pygame.draw.rect(self.screen, bg_color, btn_rect, border_radius=8)
                    pygame.draw.rect(self.screen, (50, 50, 50), btn_rect, 3, border_radius=8)

                    # Draw text
                    btn_font = pygame.font.Font(None, 36)
                    btn_text = btn_font.render(btn["text"], True, (20, 20, 20))
                    btn_text_rect = btn_text.get_rect(center=btn_rect.center)
                    self.screen.blit(btn_text, btn_text_rect)
        
        pygame.display.flip()
    
    def run(self):
        # Start with menu music
        pygame.mixer.music.load(self.music['menu'])
        pygame.mixer.music.play(-1)
        
        while True:
            # Handle events
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                
                # Handle player respawn timer
                if event.type == pygame.USEREVENT + 1:
                    if self.player and self.player.is_dead:
                        self.player.respawn()
                    
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        if self.state in ["playing", "paused"]:
                            self.pause_game()
                
                # Handle pause menu button clicks
                if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                    if self.state == "paused" and self.pause_buttons:
                        for button in self.pause_buttons:
                            if button["rect"].collidepoint(event.pos):
                                if button["action"] == "resume":
                                    self.pause_game()
                                elif button["action"] == "restart":
                                    current_level = self.level.level_number
                                    self.start_level(current_level)
                                elif button["action"] == "menu":
                                    self.return_to_menu_from_pause()
                
                # Pass events to active components
                if self.state == "menu":
                    self.menu.handle_event(event)
                elif self.state == "playing":
                    if self.player and not self.player.is_dead:
                        self.player.handle_event(event)
            
            # Update game logic
            self.update()
            
            # Draw everything
            self.draw()
            
            # Cap the framerate
            self.clock.tick(FPS)

if __name__ == "__main__":
    game = Game()
    game.run()
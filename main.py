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
                text_rect = text.get_rect(center=(WIDTH//2, HEIGHT//2))
                self.screen.blit(text, text_rect)
        
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
                    
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        if self.state in ["playing", "paused"]:
                            self.pause_game()
                
                # Pass events to active components
                if self.state == "menu":
                    self.menu.handle_event(event)
                elif self.state == "playing":
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
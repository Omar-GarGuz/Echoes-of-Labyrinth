import pygame
from settings import *

class UI:
    def __init__(self, game):
        self.game = game
        self.font = pygame.font.Font(None, 32)
        
        # Load UI elements
        self.memory_icon = pygame.image.load("assets/ui/memory_icon.png")
        self.memory_icon = pygame.transform.scale(self.memory_icon, (30, 30))
        
    def update(self):
        pass
        
    def draw(self):
        # Draw memory orbs collected
        self.draw_memory_status()
        
    def draw_memory_status(self):
        # Draw memory orb indicators
        if self.game.player and self.game.player.memories:
            memory_display_width = 40
            memory_display_height = 40
            memory_spacing = 10
            start_x = 20
            start_y = 20
            
            for i, memory in enumerate(self.game.player.memories):
                # Calculate position
                pos_x = start_x + i * (memory_display_width + memory_spacing)
                pos_y = start_y
                
                # Draw memory background
                pygame.draw.circle(
                    self.game.screen, 
                    memory.color, 
                    (pos_x + memory_display_width // 2, pos_y + memory_display_height // 2), 
                    memory_display_width // 2
                )
                
                # Draw memory icon
                self.game.screen.blit(
                    self.memory_icon, 
                    (pos_x + 5, pos_y + 5)
                )
                
                # If memory is fading, show fade effect
                if memory.is_fading:
                    fade_progress = (pygame.time.get_ticks() - memory.fade_start_time) / 2000  # 2 second fade
                    fade_alpha = int(255 * (1 - fade_progress))
                    
                    fade_surf = pygame.Surface((memory_display_width, memory_display_height), pygame.SRCALPHA)
                    fade_surf.fill((255, 255, 255, fade_alpha))
                    
                    self.game.screen.blit(
                        fade_surf, 
                        (pos_x, pos_y)
                    )
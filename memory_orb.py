import pygame
import math
from settings import *

class MemoryOrb(pygame.sprite.Sprite):
    def __init__(self, x, y, memory_type, duration=None):
        super().__init__()
        self.pos = pygame.math.Vector2(x, y)
        self.memory_type = memory_type
        self.color = MEMORY_TYPES[memory_type]['color']  # Ensure this is (R, G, B)
        self.duration = MEMORY_TYPES[memory_type]['duration'] if duration is None else duration
        
        # Animation properties
        self.radius = 15
        self.pulse_speed = 0.05
        self.pulse_size = 5
        self.pulse_offset = 0
        
        # Create rect for collision detection
        self.rect = pygame.Rect(x - self.radius, y - self.radius, 
                               self.radius * 2, self.radius * 2)
        
        # Collection properties
        self.collected = False
        self.collected_time = 0
        self.is_fading = False
        self.fade_start_time = 0
        
        # Create image for the orb
        self.image = pygame.Surface((20, 20), pygame.SRCALPHA)
        self.image.fill((255, 215, 0, 0))  # Transparent background
        pygame.draw.circle(self.image, self.color, (10, 10), 10)
        
    def collect(self):
        self.collected = True
        self.collected_time = pygame.time.get_ticks()
        
    def update(self):
        # Update pulse animation
        self.pulse_offset += self.pulse_speed
        if self.pulse_offset > 2 * 3.14159:
            self.pulse_offset = 0
            
    def draw(self, screen, offset):
        if not self.collected:
            # Calculate pulsing size
            pulse = self.radius + self.pulse_size * abs(math.sin(self.pulse_offset))
            
            # Draw outer glow with alpha
            glow_surface = pygame.Surface((int(pulse * 2), int(pulse * 2)), pygame.SRCALPHA)
            for r in range(int(pulse), int(self.radius - 2), -1):
                # Fix alpha calculation to stay within 0-255
                alpha = max(0, min(255, int(100 * (pulse - r) / self.pulse_size)))
                color = (*self.color, alpha)
                pygame.draw.circle(
                    glow_surface, 
                    color, 
                    (int(pulse), int(pulse)), 
                    r
                )
            screen.blit(glow_surface, (int(self.pos.x + offset.x - pulse), int(self.pos.y + offset.y - pulse)))
            
            # Draw inner solid circle
            pygame.draw.circle(
                screen,
                self.color,
                (int(self.pos.x + offset.x), int(self.pos.y + offset.y)), 
                self.radius - 2
            )
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
        
        # pulse animation vars
        self.radius = 15
        self.pulse_speed = 0.05
        self.pulse_size = 5
        self.pulse_offset = 0
        
        # collision box
        self.rect = pygame.Rect(x - self.radius, y - self.radius, 
                               self.radius * 2, self.radius * 2)
        
        # tracking collect/fade state
        self.collected = False
        self.collected_time = 0
        self.is_fading = False
        self.fade_start_time = 0
        
        # cassette image - same 4 all orbs regardless of color
        raw = pygame.image.load("assets/ui/memory_icon.png").convert_alpha()
        self.cassette = pygame.transform.scale(raw, (36, 36))

        # sprite groups need an image attr 2 work
        self.image = pygame.Surface((self.radius * 2, self.radius * 2), pygame.SRCALPHA)
        
    def collect(self):
        self.collected = True
        self.collected_time = pygame.time.get_ticks()
        
    def update(self):
        # make it pulse
        self.pulse_offset += self.pulse_speed
        if self.pulse_offset > 2 * 3.14159:
            self.pulse_offset = 0
            
    def draw(self, screen, offset):
        if not self.collected:
            cx = int(self.pos.x + offset.x)
            cy = int(self.pos.y + offset.y)

            # glow size changes with the pulse
            pulse = self.radius + self.pulse_size * abs(math.sin(self.pulse_offset))

            # glow behind everything
            glow_surface = pygame.Surface((int(pulse * 2), int(pulse * 2)), pygame.SRCALPHA)
            for r in range(int(pulse), int(self.radius - 2), -1):
                alpha = max(0, min(255, int(100 * (pulse - r) / self.pulse_size)))
                pygame.draw.circle(glow_surface, (*self.color, alpha),
                                   (int(pulse), int(pulse)), r)
            screen.blit(glow_surface, (cx - int(pulse), cy - int(pulse)))

            # colored circle under the cassette
            orb_r = self.radius - 2
            dark = tuple(max(0, c - 55) for c in self.color)
            pygame.draw.circle(screen, dark, (cx, cy), orb_r)
            pygame.draw.circle(screen, self.color, (cx, cy), orb_r - 2)

            # cassette on top
            cw, ch = self.cassette.get_size()
            screen.blit(self.cassette, (cx - cw // 2, cy - ch // 2))
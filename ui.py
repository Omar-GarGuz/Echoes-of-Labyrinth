import pygame
import math
from settings import *

class UI:
    def __init__(self, game):
        self.game = game
        self.font = pygame.font.Font(None, 32)

        # cassette img 4 the inventory bar
        raw = pygame.image.load("assets/ui/memory_icon.png").convert_alpha()
        self.cassette = pygame.transform.scale(raw, (36, 36))
    def update(self):
        pass
        
    def draw(self):
        # show cassettes in the hud
        self.draw_memory_status()
        
    def draw_memory_status(self):
        # show collected cassettes in the top left
        if self.game.player and self.game.player.memories:
            orb_r = 22          # circle radius
            spacing = 14
            start_x = orb_r + 10
            start_y = orb_r + 10

            for i, memory in enumerate(self.game.player.memories):
                cx = start_x + i * (orb_r * 2 + spacing)
                cy = start_y
                color = memory.color

                # glow ring behind everything
                glow_size = orb_r + 8
                glow_surf = pygame.Surface((glow_size * 2, glow_size * 2), pygame.SRCALPHA)
                for r in range(glow_size, orb_r - 1, -1):
                    alpha = max(0, min(120, int(120 * (glow_size - r) / 8)))
                    pygame.draw.circle(glow_surf, (*color, alpha),
                                       (glow_size, glow_size), r)
                self.game.screen.blit(glow_surf, (cx - glow_size, cy - glow_size))

                # colored circle
                dark = tuple(max(0, c - 55) for c in color)
                pygame.draw.circle(self.game.screen, dark, (cx, cy), orb_r)
                pygame.draw.circle(self.game.screen, color, (cx, cy), orb_r - 2)

                # cassette on top
                cw, ch = self.cassette.get_size()
                self.game.screen.blit(self.cassette, (cx - cw // 2, cy - ch // 2))

                # cover it up as it fades out
                if memory.is_fading:
                    fade_progress = (pygame.time.get_ticks() - memory.fade_start_time) / 2000
                    fade_alpha = max(0, min(180, int(180 * (1 - fade_progress))))
                    fade_surf = pygame.Surface((orb_r * 2, orb_r * 2), pygame.SRCALPHA)
                    pygame.draw.circle(fade_surf, (20, 20, 40, fade_alpha),
                                       (orb_r, orb_r), orb_r)
                    self.game.screen.blit(fade_surf, (cx - orb_r, cy - orb_r))
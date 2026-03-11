import pygame
from settings import *

class Ghost(pygame.sprite.Sprite):
    def __init__(self, x, y, patrol_left, patrol_right, speed=2):
        super().__init__()
        self.pos = pygame.math.Vector2(x, y)
        self.patrol_left = patrol_left
        self.patrol_right = patrol_right
        self.speed = speed
        self.moving_right = True

        # load the 2 horizontal frames
        frames_raw = [
            pygame.image.load(f"assets/enemies/enemy_ghost/horizontal/{i}.png").convert_alpha()
            for i in range(2)
        ]
        # scale 2 a reasonable size (same width as player, bit shorter)
        self.frames = [pygame.transform.scale(f, (50, 60)) for f in frames_raw]

        self.current_frame = 0
        self.animation_speed = 0.08
        self.image = self.frames[0]
        self.rect = self.image.get_rect(topleft=(x, y))

    def update(self):
        # walk horizontally, bounce off patrol bounds
        if self.moving_right:
            self.pos.x += self.speed
            if self.pos.x >= self.patrol_right:
                self.moving_right = False
        else:
            self.pos.x -= self.speed
            if self.pos.x <= self.patrol_left:
                self.moving_right = True

        self.rect.x = int(self.pos.x)

        # tick animation
        self.current_frame += self.animation_speed
        if self.current_frame >= len(self.frames):
            self.current_frame = 0

        frame = self.frames[int(self.current_frame)]
        # flip when going left
        if not self.moving_right:
            frame = pygame.transform.flip(frame, True, False)
        self.image = frame

    def draw(self, screen, offset):
        screen.blit(self.image, (self.rect.x + offset.x, self.rect.y + offset.y))

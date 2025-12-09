import pygame
from settings import *

class Door(pygame.sprite.Sprite):
    def __init__(self, x, y, width, height, required_memory, target_room, target_x, target_y):
        super().__init__()
        self.rect = pygame.Rect(x, y, width, height)
        self.required_memory = required_memory
        self.target_room = target_room
        self.target_x = target_x
        self.target_y = target_y
        self.is_open = False
        
        # Animation properties
        self.opening = False
        self.opening_time = 0
        self.open_duration = 500  # milliseconds
        
        # Load images
        self.closed_img = pygame.image.load("assets/objects/door_closed.png")
        self.open_img = pygame.image.load("assets/objects/door_open.png")
        self.closed_img = pygame.transform.scale(self.closed_img, (width, height))
        self.open_img = pygame.transform.scale(self.open_img, (width, height))
        
    def update(self, player):
        if not self.is_open and not self.opening:
            interact_zone = self.rect.inflate(60, 60)
            if interact_zone.colliderect(player.rect) and player.interacting:
                if self.required_memory is None or player.has_memory(self.required_memory):
                    self.opening = True
                    self.opening_time = pygame.time.get_ticks()
                    player.game.sounds['door_open'].play()
        if self.opening and not self.is_open:
            if pygame.time.get_ticks() - self.opening_time > self.open_duration:
                self.is_open = True
    
    def draw(self, screen, offset):
        if self.is_open:
            screen.blit(self.open_img, (self.rect.x + offset.x, self.rect.y + offset.y))
        else:
            screen.blit(self.closed_img, (self.rect.x + offset.x, self.rect.y + offset.y))

class Lever(pygame.sprite.Sprite):
    def __init__(self, x, y, target_id, action):
        super().__init__()
        self.rect = pygame.Rect(x, y, 40, 40)
        self.target_id = target_id
        self.action = action
        self.activated = False
        
        # Load images
        self.off_img = pygame.image.load("assets/objects/lever_off.png")
        self.on_img = pygame.image.load("assets/objects/lever_on.png")
        self.off_img = pygame.transform.scale(self.off_img, (40, 40))
        self.on_img = pygame.transform.scale(self.on_img, (40, 40))
        
    def update(self, player):
        interact_zone = self.rect.inflate(40, 40)
        if interact_zone.colliderect(player.rect) and player.interacting and not self.activated:
            self.activated = True
            player.game.sounds['switch'].play()
            for platform in player.game.level.platforms:
                if platform.id == self.target_id:
                    if self.action == "activate":
                        platform.active = True
                    elif self.action == "deactivate":
                        platform.active = False
                    elif self.action == "toggle":
                        platform.active = not platform.active
    
    def draw(self, screen, offset):
        if self.activated:
            screen.blit(self.on_img, (self.rect.x + offset.x, self.rect.y + offset.y))
        else:
            screen.blit(self.off_img, (self.rect.x + offset.x, self.rect.y + offset.y))

class Switch(pygame.sprite.Sprite):
    def __init__(self, x, y, required_memory, target_id, action):
        super().__init__()
        self.rect = pygame.Rect(x, y, 40, 40)
        self.required_memory = required_memory
        self.target_id = target_id
        self.action = action
        self.activated = False
        
        # Load images
        self.off_img = pygame.image.load("assets/objects/switch_off.png")
        self.on_img = pygame.image.load("assets/objects/switch_on.png")
        self.off_img = pygame.transform.scale(self.off_img, (40, 40))
        self.on_img = pygame.transform.scale(self.on_img, (40, 40))
        
    def update(self, player):
        interact_zone = self.rect.inflate(40, 40)
        if interact_zone.colliderect(player.rect) and player.interacting and not self.activated:
            if self.required_memory is None or player.has_memory(self.required_memory):
                self.activated = True
                player.game.sounds['switch'].play()
                for platform in player.game.level.platforms:
                    if platform.id == self.target_id:
                        if self.action == "activate":
                            platform.active = True
                        elif self.action == "deactivate":
                            platform.active = False
                        elif self.action == "toggle":
                            platform.active = not platform.active
    
    def draw(self, screen, offset):
        if self.activated:
            screen.blit(self.on_img, (self.rect.x + offset.x, self.rect.y + offset.y))
        else:
            screen.blit(self.off_img, (self.rect.x + offset.x, self.rect.y + offset.y))

class MovingPlatform(pygame.sprite.Sprite):
    def __init__(self, x, y, width, height, move_x, move_y, speed, platform_id):
        super().__init__()
        self.id = platform_id
        self.rect = pygame.Rect(x, y, width, height)
        self.start_pos = pygame.math.Vector2(x, y)
        self.move_distance = pygame.math.Vector2(move_x, move_y)
        self.speed = speed
        self.progress = 0
        self.forward = True
        self.active = False  # set true via lever/switch or JSON
        self.is_moving_platform = True
        self.prev_rect = self.rect.copy()
        self.delta = (0, 0)
        
        # Load image
        self.image = pygame.image.load("assets/objects/platform.png")
        self.image = pygame.transform.scale(self.image, (width, height))
        
    def update(self):
        self.prev_rect = self.rect.copy()
        if self.active:
            # Update platform position
            if self.forward:
                self.progress += self.speed
                if self.progress >= 1:
                    self.progress = 1
                    self.forward = False
            else:
                self.progress -= self.speed
                if self.progress <= 0:
                    self.progress = 0
                    self.forward = True
                    
            # Calculate current position
            current_x = self.start_pos.x + self.move_distance.x * self.progress
            current_y = self.start_pos.y + self.move_distance.y * self.progress
            
            # Update rect position
            self.rect.x = current_x
            self.rect.y = current_y

        # movement delta this frame
        self.delta = (self.rect.x - self.prev_rect.x, self.rect.y - self.prev_rect.y)
    
    def draw(self, screen, offset):
        screen.blit(self.image, (self.rect.x + offset.x, self.rect.y + offset.y))
import pygame
from settings import *

class Player:
    def __init__(self, game, start_pos):
        self.game = game
        
        # Player position and movement
        self.pos = pygame.math.Vector2(start_pos)
        self.vel = pygame.math.Vector2(0, 0)
        self.size = pygame.math.Vector2(PLAYER_SIZE)
        self.rect = pygame.Rect(self.pos.x, self.pos.y, self.size.x, self.size.y)
        
        # Player states
        self.facing_right = True
        self.jumping = False
        self.on_ground = False
        self.interacting = False
        
        # Animation properties
        self.current_sprite = 0
        self.animation_speed = 0.15
        self.state = "idle"  # idle, walk, jump, fall
        
        # Load sprites
        self.load_sprites()
        
        # Memory collection
        self.memories = []
        
    def load_sprites(self):
        # Load all player animations
        self.animations = {
            "idle": [pygame.image.load(f"assets/player/idle/{i}.png") for i in range(4)],
            "walk": [pygame.image.load(f"assets/player/walk/{i}.png") for i in range(6)],
            "jump": [pygame.image.load(f"assets/player/jump/{i}.png") for i in range(3)],
            "fall": [pygame.image.load(f"assets/player/fall/{i}.png") for i in range(2)]
        }
        
        # Scale all sprites
        for action in self.animations:
            for i, sprite in enumerate(self.animations[action]):
                self.animations[action][i] = pygame.transform.scale(sprite, (int(self.size.x), int(self.size.y)))
        
    def handle_event(self, event):
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE and self.on_ground:
                self.jump()
            elif event.key == pygame.K_e:
                self.interacting = True
        elif event.type == pygame.KEYUP:
            if event.key == pygame.K_e:
                self.interacting = False
    
    def jump(self):
        if self.on_ground:
            self.vel.y = -PLAYER_JUMP_STRENGTH
            self.jumping = True
            self.on_ground = False
            self.game.sounds['jump'].play()
            self.state = "jump"
    
    def collect_memory(self, memory):
        self.memories.append(memory)
        self.game.sounds['collect'].play()
        
    def has_memory(self, memory_type):
        for memory in self.memories:
            if memory.memory_type == memory_type and not memory.is_fading:
                return True
        return False
    
    def forget_memory(self, memory):
        if memory in self.memories:
            self.memories.remove(memory)
            self.game.sounds['memory_fade'].play()
            
    def update_animation(self):
        # Update animation based on current state
        self.current_sprite += self.animation_speed
        
        if self.current_sprite >= len(self.animations[self.state]):
            self.current_sprite = 0
            
        sprite = self.animations[self.state][int(self.current_sprite)]
        
        # Flip sprite if facing left
        if not self.facing_right:
            sprite = pygame.transform.flip(sprite, True, False)
            
        return sprite
    
    def update(self):
        # Update player position based on velocity
        keys = pygame.key.get_pressed()
        
        # Horizontal movement
        self.vel.x = 0
        if keys[pygame.K_LEFT] or keys[pygame.K_a]:
            self.vel.x = -PLAYER_SPEED
            self.facing_right = False
            if self.on_ground:
                self.state = "walk"
        elif keys[pygame.K_RIGHT] or keys[pygame.K_d]:
            self.vel.x = PLAYER_SPEED
            self.facing_right = True
            if self.on_ground:
                self.state = "walk"
        elif self.on_ground:
            self.state = "idle"
        
        # Apply gravity
        self.vel.y += PLAYER_GRAVITY
        
        # Update position
        self.pos.x += self.vel.x
        self.check_horizontal_collisions()
        
        self.pos.y += self.vel.y
        self.check_vertical_collisions()
        
        # Update rect
        self.rect.x = self.pos.x
        self.rect.y = self.pos.y
        
        # Update animation states
        if not self.on_ground:
            if self.vel.y < 0:
                self.state = "jump"
            else:
                self.state = "fall"
        
        # Update memory timers
        self.update_memories()
        
    def check_horizontal_collisions(self):
        # Check for collisions with tiles
        for tile in self.game.level.get_colliding_tiles(self):
            # Left collision
            if self.vel.x > 0:
                self.pos.x = tile.rect.left - self.size.x
            # Right collision
            elif self.vel.x < 0:
                self.pos.x = tile.rect.right
                
    def check_vertical_collisions(self):
        # Check for collisions with tiles
        self.on_ground = False
        for tile in self.game.level.get_colliding_tiles(self):
            # Bottom collision (landing)
            if self.vel.y > 0:
                self.pos.y = tile.rect.top - self.size.y
                self.vel.y = 0
                self.on_ground = True
                self.jumping = False
            # Top collision (hitting ceiling)
            elif self.vel.y < 0:
                self.pos.y = tile.rect.bottom
                self.vel.y = 0
                
    def update_memories(self):
        # Check if any memories need to fade
        for memory in self.memories[:]:  # Copy list to safely modify during iteration
            if memory.duration and pygame.time.get_ticks() - memory.collected_time > memory.duration:
                if not memory.is_fading:
                    memory.is_fading = True
                    memory.fade_start_time = pygame.time.get_ticks()
                
                # Check if fade is complete
                if pygame.time.get_ticks() - memory.fade_start_time > 2000:  # 2 second fade
                    self.forget_memory(memory)
    
    def draw(self, screen):
        # Draw the player
        sprite = self.update_animation()
        screen.blit(sprite, self.rect)
        
        # For debugging, draw the collision box
        # pygame.draw.rect(screen, RED, self.rect, 2)
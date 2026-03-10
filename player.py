import pygame
from settings import *

class Player:
    def __init__(self, game, start_pos):
        self.game = game
        
        # position and velocity
        self.pos = pygame.math.Vector2(start_pos)
        self.vel = pygame.math.Vector2(0, 0)
        self.size = pygame.math.Vector2(PLAYER_SIZE)
        self.rect = pygame.Rect(self.pos.x, self.pos.y, self.size.x, self.size.y)
        
        # remember where we started 4 respawn
        self.spawn_point = pygame.math.Vector2(start_pos)
        
        # flags 4 what the player is doing
        self.facing_right = True
        self.jumping = False
        self.on_ground = False
        self.interacting = False
        self.on_moving_platform = None
        self.is_dead = False
        
        # animation stuff
        self.current_sprite = 0
        self.animation_speed = 0.05
        self.state = "idle"  # idle, walk, jump, fall
        
        # bring in all the sprites
        self.load_sprites()
        
        # memories the player has collected
        self.memories = []
        
    def load_sprites(self):
        # load every animation from disk
        self.animations = {
            "idle": [pygame.image.load(f"assets/player/idle/{i}.png") for i in range(4)],
            "walk": [pygame.image.load(f"assets/player/walk/{i}.png") for i in range(6)],
            "jump": [pygame.image.load(f"assets/player/jump/{i}.png") for i in range(2)],
            "fall": [pygame.image.load(f"assets/player/fall/{i}.png") for i in range(2)]
        }
        
        # resize all of them 2 match player size
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
        # pick the right frame 4 the current state
        self.current_sprite += self.animation_speed
        
        if self.current_sprite >= len(self.animations[self.state]):
            self.current_sprite = 0
            
        sprite = self.animations[self.state][int(self.current_sprite)]
        
        # flip it if going left
        if not self.facing_right:
            sprite = pygame.transform.flip(sprite, True, False)
            
        return sprite
    
    def check_death(self):
        # if u fall below this y value, u die
        death_y = 800  # change this if the level is taller
        
        if self.pos.y > death_y:
            self.die()
    
    def die(self):
        if not self.is_dead:
            self.is_dead = True
            # TODO: add a death sound lol
            # self.game.sounds['death'].play()
            
            # wait a sec then respawn
            pygame.time.set_timer(pygame.USEREVENT + 1, 1000)  # 1000ms = 1 second
    
    def respawn(self):
        pygame.time.set_timer(pygame.USEREVENT + 1, 0)  # stop the timer, dont want it firing again
        self.pos = pygame.math.Vector2(self.spawn_point)
        self.vel = pygame.math.Vector2(0, 0)
        self.rect.x = self.pos.x
        self.rect.y = self.pos.y
        self.is_dead = False
        self.on_ground = False
        self.jumping = False
        
        # optional: lose ur memories on death - uncomment 2 enable
        #self.memories.clear()
    
    def update(self):
        if self.is_dead:
            return  # skip everything when dead
        
        keys = pygame.key.get_pressed()

        # left and right movement
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

        # pull down every frame
        self.vel.y += PLAYER_GRAVITY

        # step 1: move horizontal
        self.pos.x += self.vel.x
        self.rect.x = self.pos.x
        self.check_horizontal_collisions()

        # step 2: move vertical
        self.pos.y += self.vel.y
        self.rect.y = self.pos.y
        self.check_vertical_collisions()

        # sync rect 2 pos
        self.rect.x = self.pos.x
        self.rect.y = self.pos.y

        # update animation based on velocity
        if not self.on_ground:
            self.state = "jump" if self.vel.y < 0 else "fall"

        # fell 2 far?
        self.check_death()
        
        # tick the memory timers
        self.update_memories()

    def check_horizontal_collisions(self):
        for tile in self.game.level.get_colliding_tiles(self):
            if self.vel.x > 0:
                self.pos.x = tile.rect.left - self.size.x
            elif self.vel.x < 0:
                self.pos.x = tile.rect.right
        self.rect.x = self.pos.x  # keep in sync

    def check_vertical_collisions(self):
        self.on_ground = False
        landed_on_platform = None
        
        # need prev bottom 4 one-way platform check
        prev_bottom = self.rect.bottom - self.vel.y

        for tile in self.game.level.get_colliding_tiles(self):
            # is this a platform u can jump thru from below?
            is_one_way = hasattr(tile, 'one_way') and tile.one_way
            
            if self.vel.y > 0:  # falling / landing
                # one-way: only land if coming from above
                if is_one_way:
                    if prev_bottom <= tile.rect.top + 5:  # lil tolerance
                        self.pos.y = tile.rect.top - self.size.y
                        self.vel.y = 0
                        self.on_ground = True
                        self.jumping = False
                        if hasattr(tile, "is_moving_platform") and tile.is_moving_platform:
                            landed_on_platform = tile
                else:
                    # solid tile - always lands
                    # the rect.bottom check prevents teleporting thru walls
                    if self.rect.bottom <= tile.rect.top + abs(self.vel.y) + 5:
                        self.pos.y = tile.rect.top - self.size.y
                        self.vel.y = 0
                        self.on_ground = True
                        self.jumping = False
                        if hasattr(tile, "is_moving_platform") and tile.is_moving_platform:
                            landed_on_platform = tile
            elif self.vel.y < 0 and not is_one_way:  # hit the ceiling
                self.pos.y = tile.rect.bottom
                self.vel.y = 0

        # stick 2 the moving platform
        if landed_on_platform:
            dx, dy = landed_on_platform.delta
            self.pos.x += dx
            self.pos.y += dy
            self.on_moving_platform = landed_on_platform
        else:
            self.on_moving_platform = None

        self.rect.y = int(self.pos.y)  # int cast fixes subpixel jitter
                
    def update_memories(self):
        # check each memory - copy the list so we can remove while looping
        for memory in self.memories[:]:
            if memory.duration and pygame.time.get_ticks() - memory.collected_time > memory.duration:
                if not memory.is_fading:
                    memory.is_fading = True
                    memory.fade_start_time = pygame.time.get_ticks()
                
                # 2 seconds 2 fully fade, then remove it
                if pygame.time.get_ticks() - memory.fade_start_time > 2000:
                    self.forget_memory(memory)
    
    def draw(self, screen):
        sprite = self.update_animation()
        offset = self.game.level.camera_offset
        screen.blit(sprite, (self.rect.x + offset.x, self.rect.y + offset.y))
        # debug: uncomment 2 see the hitbox
        # pygame.draw.rect(screen, RED, self.rect.move(offset.x, offset.y), 2)
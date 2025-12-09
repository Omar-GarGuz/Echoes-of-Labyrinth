import pygame
import json
import os
from settings import *
from memory_orb import MemoryOrb
from interactive_objects import Door, Lever, Switch, MovingPlatform

class Tile(pygame.sprite.Sprite):
    def __init__(self, x, y, tile_type):
        super().__init__()
        self.tile_type = tile_type
        self.image = pygame.image.load(f"assets/tiles/{tile_type}.png")
        self.image = pygame.transform.scale(self.image, (TILE_SIZE, TILE_SIZE))
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y

class Level:
    def __init__(self, game, level_number):
        self.game = game
        self.level_number = level_number
        
        # Sprite groups
        self.tiles = pygame.sprite.Group()
        self.background_tiles = pygame.sprite.Group()
        self.memory_orbs = pygame.sprite.Group()
        self.doors = pygame.sprite.Group()
        self.levers = pygame.sprite.Group()
        self.switches = pygame.sprite.Group()
        self.platforms = pygame.sprite.Group()
        self.enemies = pygame.sprite.Group()
        
        # Current room
        self.current_room = "start"
        self.rooms = {}
        
        # Camera
        self.camera_offset = pygame.math.Vector2(0, 0)
        
        # Load level
        self.load_level()
    
    def load_level(self):
        # Load level data from JSON file
        with open(f"assets/levels/level_{self.level_number}.json", 'r') as file:
            level_data = json.load(file)
            
        # Load rooms
        self.rooms = level_data["rooms"]
        
        # Set player start position
        self.player_start_pos = (level_data["player_start"]["x"], level_data["player_start"]["y"])
        
        # Load initial room
        self.load_room(self.current_room)
    
    def load_room(self, room_name):
        # Clear existing room objects
        self.tiles.empty()
        self.background_tiles.empty()
        self.memory_orbs.empty()
        self.doors.empty()
        self.levers.empty()
        self.switches.empty()
        self.platforms.empty()
        self.enemies.empty()
        
        # Get room data
        room_data = self.rooms[room_name]
        
        # Load tiles
        for layer_name, layer in room_data["layers"].items():
            for y, row in enumerate(layer):
                for x, tile_id in enumerate(row):
                    if tile_id != 0:  # 0 means no tile
                        tile_type = room_data["tile_mapping"][str(tile_id)]
                        tile_x = x * TILE_SIZE
                        tile_y = y * TILE_SIZE
                        
                        if layer_name == "foreground":
                            tile = Tile(tile_x, tile_y, tile_type)
                            self.tiles.add(tile)
                        else:  # background
                            bg_tile = Tile(tile_x, tile_y, tile_type)
                            self.background_tiles.add(bg_tile)
        
        # Load memory orbs
        for orb_data in room_data.get("memory_orbs", []):
            orb = MemoryOrb(
                orb_data["x"], 
                orb_data["y"],
                orb_data["memory_type"],
                orb_data.get("duration", None)
            )
            self.memory_orbs.add(orb)
            
        # Load doors
        for door_data in room_data.get("doors", []):
            door = Door(
                door_data["x"],
                door_data["y"],
                door_data["width"],
                door_data["height"],
                door_data["required_memory"],
                door_data["target_room"],
                door_data.get("target_x", 0),
                door_data.get("target_y", 0)
            )
            self.doors.add(door)
            
        # Load levers
        for lever_data in room_data.get("levers", []):
            lever = Lever(
                lever_data["x"],
                lever_data["y"],
                lever_data["target_id"],
                lever_data["action"]
            )
            self.levers.add(lever)
            
        # Load switches
        for switch_data in room_data.get("switches", []):
            switch = Switch(
                switch_data["x"],
                switch_data["y"],
                switch_data["required_memory"],
                switch_data["target_id"],
                switch_data["action"]
            )
            self.switches.add(switch)
            
        # Load moving platforms
        for platform_data in room_data.get("moving_platforms", []):
            platform = MovingPlatform(
                platform_data["x"],
                platform_data["y"],
                platform_data["width"],
                platform_data["height"],
                platform_data["move_x"],
                platform_data["move_y"],
                platform_data["speed"],
                platform_data["id"]
            )
            self.platforms.add(platform)
            
        # Update current room
        self.current_room = room_name
    
    def get_colliding_tiles(self, entity):
        """Returns all tiles that collide with the entity."""
        colliding_tiles = []
        
        for tile in self.tiles:
            if entity.rect.colliderect(tile.rect):
                colliding_tiles.append(tile)
                
        for platform in self.platforms:
            if entity.rect.colliderect(platform.rect):
                colliding_tiles.append(platform)
                
        return colliding_tiles
        
    def update(self, player):
        # Update all sprites
        self.memory_orbs.update()
        self.doors.update(player)
        self.levers.update(player)
        self.switches.update(player)
        self.platforms.update()
        self.enemies.update(player)
        
        # Check for memory orb collection
        for orb in self.memory_orbs:
            if player.rect.colliderect(orb.rect):
                player.collect_memory(orb)
                orb.collect()
                self.memory_orbs.remove(orb)
                
        # Check if player entered a door
        for door in self.doors:
            if door.is_open and player.rect.colliderect(door.rect):
                if door.target_room:
                    # Transport player to new room
                    self.load_room(door.target_room)
                    player.pos.x = door.target_x
                    player.pos.y = door.target_y
                    player.rect.x = player.pos.x
                    player.rect.y = player.pos.y
                    break

        # Update camera to follow player
        target_x = WIDTH / 2 - player.rect.centerx
        target_y = HEIGHT / 2 - player.rect.centery
        
        # After computing target_x/target_y:
        level_width = max(t.rect.right for t in self.tiles) if self.tiles else WIDTH
        level_height = max(t.rect.bottom for t in self.tiles) if self.tiles else HEIGHT

        self.camera_offset.x += (target_x - self.camera_offset.x) * 0.1
        self.camera_offset.y += (target_y - self.camera_offset.y) * 0.1

        # Clamp so we don't show beyond level bounds
        min_x = min(0, WIDTH - level_width)
        min_y = min(0, HEIGHT - level_height)
        self.camera_offset.x = max(min_x, min(0, self.camera_offset.x))
        self.camera_offset.y = max(min_y, min(0, self.camera_offset.y))
    
    def draw(self, screen):
        # Draw background
        for tile in self.background_tiles:
            screen.blit(tile.image, (tile.rect.x + self.camera_offset.x, 
                                      tile.rect.y + self.camera_offset.y))
        
        # Draw tiles
        for tile in self.tiles:
            screen.blit(tile.image, (tile.rect.x + self.camera_offset.x, 
                                      tile.rect.y + self.camera_offset.y))
        
        # Draw memory orbs
        for orb in self.memory_orbs:
            orb.draw(screen, self.camera_offset)
        
        # Draw interactive objects
        for door in self.doors:
            door.draw(screen, self.camera_offset)
            
        for lever in self.levers:
            lever.draw(screen, self.camera_offset)
            
        for switch in self.switches:
            switch.draw(screen, self.camera_offset)
            
        for platform in self.platforms:
            platform.draw(screen, self.camera_offset)
        
        # Draw enemies
        for enemy in self.enemies:
            enemy.draw(screen, self.camera_offset)
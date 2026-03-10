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
        
        # sprite groups 4 everything
        self.tiles = pygame.sprite.Group()
        self.background_tiles = pygame.sprite.Group()
        self.memory_orbs = pygame.sprite.Group()
        self.doors = pygame.sprite.Group()
        self.levers = pygame.sprite.Group()
        self.switches = pygame.sprite.Group()
        self.platforms = pygame.sprite.Group()

        # signs are just images, not sprites
        self.signs = []
        
        # track which room we're in
        self.current_room = "start"
        self.rooms = {}
        
        # camera 4 scrolling
        self.camera_offset = pygame.math.Vector2(0, 0)
        
        # kick off the load
        self.load_level()
    
    def load_level(self):
        # read the JSON file 4 this level
        with open(f"assets/levels/level_{self.level_number}.json", 'r') as file:
            level_data = json.load(file)
            
        # grab all the room data
        self.rooms = level_data["rooms"]
        
        # where does the player spawn?
        self.player_start_pos = (level_data["player_start"]["x"], level_data["player_start"]["y"])
        
        # load the starting room
        self.load_room(self.current_room)
    
    def load_room(self, room_name):
        # wipe everything b4 loading the new room
        self.tiles.empty()
        self.background_tiles.empty()
        self.memory_orbs.empty()
        self.doors.empty()
        self.levers.empty()
        self.switches.empty()
        self.platforms.empty()
        self.signs = []
        
        # grab this room's data from the dict
        room_data = self.rooms[room_name]
        
        # build the tile grid from the 2d arrays
        for layer_name, layer in room_data["layers"].items():
            for y, row in enumerate(layer):
                for x, tile_id in enumerate(row):
                    if tile_id != 0:  # 0 = empty, skip it
                        tile_type = room_data["tile_mapping"][str(tile_id)]
                        tile_x = x * TILE_SIZE
                        tile_y = y * TILE_SIZE
                        
                        if layer_name == "foreground":
                            tile = Tile(tile_x, tile_y, tile_type)
                            self.tiles.add(tile)
                        else:  # background layer
                            bg_tile = Tile(tile_x, tile_y, tile_type)
                            self.background_tiles.add(bg_tile)
        
        # spawn the cassettes
        for orb_data in room_data.get("memory_orbs", []):
            orb = MemoryOrb(
                orb_data["x"], 
                orb_data["y"],
                orb_data["memory_type"],
                orb_data.get("duration", None)
            )
            self.memory_orbs.add(orb)
            
        # add doors
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
            
        # add levers
        for lever_data in room_data.get("levers", []):
            lever = Lever(
                lever_data["x"],
                lever_data["y"],
                lever_data["target_id"],
                lever_data["action"]
            )
            self.levers.add(lever)
            
        # add switches
        for switch_data in room_data.get("switches", []):
            switch = Switch(
                switch_data["x"],
                switch_data["y"],
                switch_data["required_memory"],
                switch_data["target_id"],
                switch_data["action"]
            )
            self.switches.add(switch)
            
        # add moving platforms
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
            platform.active = platform_data.get("active", False)  # can start active if json says so
            self.platforms.add(platform)
            
        # load sign images (just load + store, no logic)
        for sign_data in room_data.get("signs", []):
            img = pygame.image.load(f"assets/{sign_data['image']}")
            img = pygame.transform.scale(img, (sign_data["width"], sign_data["height"]))
            rect = img.get_rect(topleft=(sign_data["x"], sign_data["y"]))
            self.signs.append({"image": img, "rect": rect})

        # done - save which room we're in
        self.current_room = room_name
    
    def get_colliding_tiles(self, entity):
        # returns everything the entity is touching
        colliding_tiles = []
        
        for tile in list(self.tiles):
            if entity.rect.colliderect(tile.rect):
                colliding_tiles.append(tile)
                
        for platform in list(self.platforms):
            if entity.rect.colliderect(platform.rect):
                colliding_tiles.append(platform)
                
        return colliding_tiles
        
    def update(self, player):
        # tick everything
        self.memory_orbs.update()
        self.doors.update(player)
        self.levers.update(player)
        self.switches.update(player)
        self.platforms.update()
        
        # did player walk into a cassette?
        for orb in list(self.memory_orbs):
            if player.rect.colliderect(orb.rect):
                player.collect_memory(orb)
                orb.collect()
                self.memory_orbs.remove(orb)
                
        # did player go thru a door?
        for door in list(self.doors):
            if door.is_open and player.rect.colliderect(door.rect):
                if door.target_room:
                    # teleport 2 new room
                    self.load_room(door.target_room)
                    player.pos.x = door.target_x
                    player.pos.y = door.target_y
                    player.rect.x = player.pos.x
                    player.rect.y = player.pos.y
                    break

        # camera lerps toward player
        target_x = WIDTH / 2 - player.rect.centerx
        target_y = HEIGHT / 2 - player.rect.centery
        
        # get level size 4 clamping
        level_width = max(t.rect.right for t in self.tiles) if self.tiles else WIDTH
        level_height = max(t.rect.bottom for t in self.tiles) if self.tiles else HEIGHT

        self.camera_offset.x += (target_x - self.camera_offset.x) * 0.1
        self.camera_offset.y += (target_y - self.camera_offset.y) * 0.1

        # clamp so we dont scroll past the edges
        min_x = min(0, WIDTH - level_width)
        min_y = min(0, HEIGHT - level_height)
        self.camera_offset.x = max(min_x, min(0, self.camera_offset.x))
        self.camera_offset.y = max(min_y, min(0, self.camera_offset.y))
    
    def draw(self, screen):
        # bg layer first
        for tile in self.background_tiles:
            screen.blit(tile.image, (tile.rect.x + self.camera_offset.x, 
                                      tile.rect.y + self.camera_offset.y))
        
        # then foreground tiles
        for tile in self.tiles:
            screen.blit(tile.image, (tile.rect.x + self.camera_offset.x, 
                                      tile.rect.y + self.camera_offset.y))
        
        # cassettes
        for orb in self.memory_orbs:
            orb.draw(screen, self.camera_offset)
        
        # all the interactive stuff
        for door in self.doors:
            door.draw(screen, self.camera_offset)
            
        for lever in self.levers:
            lever.draw(screen, self.camera_offset)
            
        for switch in self.switches:
            switch.draw(screen, self.camera_offset)
            
        for platform in self.platforms:
            platform.draw(screen, self.camera_offset)

        # signs on top of everything
        for sign in self.signs:
            screen.blit(sign["image"], (sign["rect"].x + self.camera_offset.x,
                                        sign["rect"].y + self.camera_offset.y))
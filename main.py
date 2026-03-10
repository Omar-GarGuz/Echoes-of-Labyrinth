import pygame
import sys
import os
from settings import *
from player import Player
from level import Level
from ui import UI
from menu import Menu

class Game:
    def __init__(self):
        # init pygame
        pygame.init()
        pygame.mixer.init()
        
        # set up display
        self.screen = pygame.display.set_mode((WIDTH, HEIGHT))
        pygame.display.set_caption("Echoes of the Labyrinth")
        
        # set up the clock
        self.clock = pygame.time.Clock()
        
        # game states
        self.state = "menu"  # menu, story, playing, paused, game_over

        # story initial screen
        self.story_image = None
        
        # sound settings (MOVE THIS BEFORE load_assets)
        self.sound_volume = 0.7
        self.music_volume = 0.5
        
        # load assets
        self.load_assets()
        
        # create instances
        self.menu = Menu(self)
        self.ui = UI(self)
        self.level = None
        self.player = None
        
        # pause menu buttons
        self.pause_buttons = []
        
        # set music volume after loading
        pygame.mixer.music.set_volume(self.music_volume)
        
    def load_assets(self):
        # load all the sounds
        self.sounds = {
            'jump': pygame.mixer.Sound('assets/sounds/jump.wav'),
            'collect': pygame.mixer.Sound('assets/sounds/collect.wav'),
            'door_open': pygame.mixer.Sound('assets/sounds/door_open.wav'),
            'memory_fade': pygame.mixer.Sound('assets/sounds/memory_fade.wav'),
            'switch': pygame.mixer.Sound('assets/sounds/switch.wav')
        }
        
        for sound in self.sounds.values():
            sound.set_volume(self.sound_volume)
        
        # load music, 4 more music we have 2 rename the level#mp3
        self.music = {
            'menu': 'assets/music/menu_theme.mp3',
            'level1': 'assets/music/level1.mp3',
        }
    
    def start_level(self, level_number):
        self.level = Level(self, level_number)
        self.player = Player(self, self.level.player_start_pos)
        self.state = "playing"
        
        # play the music 4 this level
        pygame.mixer.music.load(self.music[f'level{level_number}'])
        pygame.mixer.music.play(-1)
    
    def pause_game(self):
        if self.state == "playing":
            self.state = "paused"
            pygame.mixer.music.pause()
        elif self.state == "paused":
            self.state = "playing"
            pygame.mixer.music.unpause()
    
    def show_story(self):
        """Show intro story screen before level start"""
        img = pygame.image.load("assets/objects/initial_sign.png").convert_alpha()
        orig_w, orig_h = img.get_size()
        max_h = int(HEIGHT * 0.80)
        scale = max_h / orig_h
        self.story_image = pygame.transform.scale(img, (int(orig_w * scale), int(orig_h * scale)))
        self.state = "story"

    def return_to_menu_from_pause(self):
        """Return to main menu from pause screen"""
        self.level = None
        self.player = None
        self.state = "menu"
        self.menu.showing_controls = False
        try:
            pygame.mixer.music.load(self.music['menu'])
            pygame.mixer.music.play(-1)
        except Exception:
            pass
    
    def update(self):
        if self.state == "menu":
            self.menu.update()
        elif self.state == "story":
            pass  # nothing 2 update, just sitting there
        elif self.state == "playing":
            self.player.update()
            self.level.update(self.player)
            self.ui.update()
    
    def draw(self):
        self.screen.fill(BG_COLOR)
        
        if self.state == "menu":
            self.menu.draw()
        elif self.state == "story":
            self._draw_story()
        elif self.state == "playing" or self.state == "paused":
            self.level.draw(self.screen)
            self.player.draw(self.screen)
            self.ui.draw()
            
            if self.state == "paused":
                # dark overlay so it looks paused
                pause_surf = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
                pause_surf.fill((0, 0, 0, 128))
                self.screen.blit(pause_surf, (0, 0))
                
                # big PAUSED text
                font = pygame.font.Font(None, 72)
                text = font.render("PAUSED", True, WHITE)
                text_rect = text.get_rect(center=(WIDTH//2, HEIGHT//2 - 100))
                self.screen.blit(text, text_rect)

                # button size stuff
                btn_w, btn_h = 220, 56
                btn_spacing = 20
                center_x = WIDTH // 2
                start_y = HEIGHT // 2 - 20

                # the 3 pause buttons
                buttons = [
                    {"text": "Resume", "y_offset": 0, "action": "resume"},
                    {"text": "Restart Level", "y_offset": btn_h + btn_spacing, "action": "restart"},
                    {"text": "Main Menu", "y_offset": (btn_h + btn_spacing) * 2, "action": "menu"}
                ]

                # rebuild every frame lol
                self.pause_buttons = []
                mouse_pos = pygame.mouse.get_pos()

                for btn in buttons:
                    btn_x = center_x - btn_w // 2
                    btn_y = start_y + btn["y_offset"]
                    btn_rect = pygame.Rect(btn_x, btn_y, btn_w, btn_h)
                    
                    # save the rect so clicks work later
                    self.pause_buttons.append({"rect": btn_rect, "action": btn["action"]})

                    # is the mouse hovering this button?
                    is_hover = btn_rect.collidepoint(mouse_pos)
                    
                    # draw the button bg + border
                    bg_color = (220, 220, 220) if is_hover else (200, 200, 200)
                    pygame.draw.rect(self.screen, bg_color, btn_rect, border_radius=8)
                    pygame.draw.rect(self.screen, (50, 50, 50), btn_rect, 3, border_radius=8)

                    # put the label on it
                    btn_font = pygame.font.Font(None, 36)
                    btn_text = btn_font.render(btn["text"], True, (20, 20, 20))
                    btn_text_rect = btn_text.get_rect(center=btn_rect.center)
                    self.screen.blit(btn_text, btn_text_rect)
        
        pygame.display.flip()

    def _draw_story(self):
        self.screen.fill((10, 8, 20))
        if self.story_image:
            img_rect = self.story_image.get_rect(center=(WIDTH // 2, HEIGHT // 2 - 20))
            self.screen.blit(self.story_image, img_rect)
        font = pygame.font.Font(None, 34)
        prompt = font.render("Press any key to begin...", True, (170, 170, 170))
        self.screen.blit(prompt, prompt.get_rect(center=(WIDTH // 2, HEIGHT - 40)))

    def run(self):
        # kick things off with menu music
        pygame.mixer.music.load(self.music['menu'])
        pygame.mixer.music.play(-1)
        
        while True:
            # handle all input events
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                
                # timer fires when its time 2 respawn
                if event.type == pygame.USEREVENT + 1:
                    if self.player and self.player.is_dead:
                        self.player.respawn()
                    
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        if self.state in ["playing", "paused"]:
                            self.pause_game()
                
                # snapshot state b4 any transitions - prevents click fallthrough bugs
                event_state = self.state

                # handle pause button clicks
                if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                    if event_state == "paused" and self.pause_buttons:
                        for button in self.pause_buttons:
                            if button["rect"].collidepoint(event.pos):
                                if button["action"] == "resume":
                                    self.pause_game()
                                elif button["action"] == "restart":
                                    current_level = self.level.level_number
                                    self.start_level(current_level)
                                elif button["action"] == "menu":
                                    self.return_to_menu_from_pause()
                                break

                # route events 2 whoever needs them
                if event_state == "story":
                    if event.type in (pygame.KEYDOWN, pygame.MOUSEBUTTONDOWN):
                        self.start_level(1)
                elif event_state == "menu":
                    self.menu.handle_event(event)
                elif event_state == "playing":
                    if self.player and not self.player.is_dead:
                        self.player.handle_event(event)
            
            # update all the game logic
            self.update()
            
            # draw all the stuff
            self.draw()
            
            # cap it at FPS
            self.clock.tick(FPS)

if __name__ == "__main__":
    game = Game()
    game.run()
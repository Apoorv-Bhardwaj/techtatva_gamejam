"""
RENDER GAMEJAM WOLF GAME
APOORV BHARDWAJ 
"""

import os
import sys
import random
import math
import heapq
import pygame
from pygame.math import Vector2



ASSET_DIR = os.path.join(os.path.dirname(__file__), 'assets')
MASTER_SHEET = os.path.join(ASSET_DIR, 'player', 'zamc1.png')
ENEMY_SPRITES_DIR = os.path.join(ASSET_DIR, 'enemies')
HEART_IMG = os.path.join(ASSET_DIR, 'ui', 'heart.png')
MENU_BG = os.path.join(ASSET_DIR, 'ui', 'menu_bg.png')
WIN_IMG = os.path.join(ASSET_DIR, 'ui', 'youwin.png')
DIED_IMG = os.path.join(ASSET_DIR, 'ui', 'youdied.png')
START_BTN_IMG = os.path.join(ASSET_DIR, 'ui', 'start.png')
BACK_BTN_IMG = os.path.join(ASSET_DIR, 'ui', 'back.png')

GROUND_TEXTURE = os.path.join(ASSET_DIR, 'ui', 'parallax_bg.png')


SFX_WALKING = os.path.join(ASSET_DIR, 'sound', 'walking.mp3')
SFX_RUNNING = os.path.join(ASSET_DIR, 'sound', 'running.mp3')
SFX_HURT = os.path.join(ASSET_DIR, 'sound', 'rds.mp3')
SFX_HEAL = os.path.join(ASSET_DIR, 'sound', 'heal.mp3')
SFX_HOWL = os.path.join(ASSET_DIR, 'sound', 'howl.mp3')
SFX_PUSHBACK = os.path.join(ASSET_DIR, 'sound', 'pushback.mp3')
SFX_RIP = os.path.join(ASSET_DIR, 'sound', 'rip.mp3')

MUSIC_MENU = os.path.join(ASSET_DIR, 'sound', 'menu.mp3')
MUSIC_DAY = os.path.join(ASSET_DIR, 'sound', 'day.mp3')
MUSIC_NIGHT = os.path.join(ASSET_DIR, 'sound', 'night1.wav')
MUSIC_RESPAWN = os.path.join(ASSET_DIR, 'sound', 'respawn.mp3')
MUSIC_YOUWON = os.path.join(ASSET_DIR, 'sound', 'youwon.mp3')

FRAME_WIDTH = 64
FRAME_HEIGHT = 64
SHEET_SCALE = 1.0


PLAYER_SHEET_LAYOUT = [
    {'row': 2, 'state': 'idle', 'facing': 'down',  'frames': 1},
    {'row': 1, 'state': 'idle', 'facing': 'left',  'frames': 1},
    {'row': 3, 'state': 'idle', 'facing': 'right', 'frames': 1},
    {'row': 0, 'state': 'idle', 'facing': 'up',    'frames': 1},
    {'row': 2, 'state': 'run',  'facing': 'down',  'frames': 9},
    {'row': 1, 'state': 'run',  'facing': 'left',  'frames': 9},
    {'row': 3, 'state': 'run',  'facing': 'right', 'frames': 9},
    {'row': 0, 'state': 'run',  'facing': 'up',    'frames': 9},
]


PLAYER_NIGHT_LAYOUT = [
    {'row': 2, 'state': 'idle', 'facing': 'down',  'frames': 1},
    {'row': 3, 'state': 'idle', 'facing': 'left',  'frames': 1},
    {'row': 1, 'state': 'idle', 'facing': 'right', 'frames': 1},
    {'row': 0, 'state': 'idle', 'facing': 'up',    'frames': 1},
    {'row': 2, 'state': 'run',  'facing': 'down',  'frames': 3},
    {'row': 3, 'state': 'run',  'facing': 'left',  'frames': 3},
    {'row': 1, 'state': 'run',  'facing': 'right', 'frames': 3},
    {'row': 0, 'state': 'run',  'facing': 'up',    'frames': 3},
]


PLAYER_TRANSITION_LAYOUT = [
    {'row': 2, 'state': 'transition', 'facing': 'down',  'frames': 9},
    {'row': 1, 'state': 'transition', 'facing': 'left',  'frames': 9},
    {'row': 3, 'state': 'transition', 'facing': 'right', 'frames': 9},
    {'row': 0, 'state': 'transition', 'facing': 'up',    'frames': 9},
]
0
ENEMY_SHEET_LAYOUT = [
    {'row': 2, 'state': 'idle', 'facing': 'down',  'frames': 1},
    {'row': 1, 'state': 'idle', 'facing': 'left',  'frames': 1},
    {'row': 3, 'state': 'idle', 'facing': 'right', 'frames': 1},
    {'row': 0, 'state': 'idle', 'facing': 'up',    'frames': 1},
    {'row': 2, 'state': 'run',  'facing': 'down',  'frames': 9},
    {'row': 1, 'state': 'run',  'facing': 'left',  'frames': 9},
    {'row': 3, 'state': 'run',  'facing': 'right', 'frames': 9},
    {'row': 0, 'state': 'run',  'facing': 'up',    'frames': 9},
]

FRAME_DURATION = {'idle': 220, 'run': 100, 'transition': 140}
SCREEN_SIZE = (800, 600)
WORLD_SIZE = (2000, 2000)
FPS = 60
MAX_SPEED = 250
ACCELERATION = 1200.0
FRICTION = 2000.0
KNOCKBACK_SPEED = 440.0
OBSTACLE_COUNT = 60
OBSTACLE_MIN_DIST = 140
ENEMY_COUNT = 12
ENEMY_SPAWN_MIN_DIST = 300
ENEMY_MAX_SPEED = 150
ENEMY_ACCELERATION = 900.0
NAV_CELL_SIZE = 48
NAV_EXPAND_CELLS = 1
PATH_RECALC_INTERVAL = 0.85
PLAYER_MOVE_REPATH_DIST = 64
SEPARATION_RADIUS = 36.0
SEPARATION_FORCE = 420.0
PLAYER_MAX_HEARTS = 5
HIT_FLASH_MS = 200
SPRINT_MULTIPLIER = 1.60
STAMINA_MAX = 5.0
STAMINA_DRAIN_PER_SEC = 2.5
STAMINA_RECOVER_PER_SEC = 0.3
STAMINA_MIN_TO_SPRINT = 0.2
DAY_LENGTH = 20.0            # How long daytime lasts (seconds)
NIGHT_LENGTH = 12.0          # How long nighttime lasts (seconds)
TRANSITION_MS = 560          # How long the transformation animation plays (milliseconds)
DARK_ALPHA = 190            # How dark the screen gets at night (0-255)
CUTSCENE_TEXT_SPEED = 25     # Milliseconds per character
CUTSCENE_BG_COLOR = (20, 20, 40, 220)
CUTSCENE_BORDER_COLOR = (200, 180, 100)
CUTSCENE_TEXT_COLOR = (255, 255, 255)
SKY_COLORS = {
    'sunrise': (255, 140, 80),      # Orange sunrise
    'afternoon': (255, 220, 100),   # Yellow afternoon
    'sunset': (255, 120, 60),       # Orange sunset
    'night': (40, 60, 120)          # Blue night
}
SFX_VOLUME = {
    'walking': 0.3,      # Walking footsteps
    'running': 0.4,      # Running footsteps
    'hurt': 1,         # Player takes damage
    'heal': 2,         # Player gains health
    'howl': 1,         # Night transformation
    'pushback': 0.5,     # Hit obstacle
    'rip': 1,          # Enemy defeated
}
# Music Volume (background music)
MUSIC_VOLUME = {
    'menu': 0.5,         # Menu screen music
    'day': 0.4,          # Daytime music
    'night': 0.4,        # Nighttime music
    'respawn': 0.5,      # Death screen music
    'youwon': 0.6,       # Victory screen music
}
MASTER_SFX_VOLUME = 1.0    # Overall sound effects volume multiplier
MASTER_MUSIC_VOLUME = 1.0  # Overall music volume multiplier
CAMERA_SMOOTHING = 0.1      # Lower = smoother (0.05-0.2 recommended)
CAMERA_LOOKAHEAD = 80       # Pixels ahead of player movement direction
ENABLE_VIGNETTE = True          # Darkens screen edges
ENABLE_CHROMATIC_ABERRATION = False  # Slight color splitting effect
ENABLE_SCANLINES = False        # Retro scanline effect (subtle)
ENABLE_BLOOM = True             # Glow effect on bright areas
ENABLE_CAMERA_SHAKE = True      # Screen shake on hits
VIGNETTE_INTENSITY = 0.6        # 0.0 = none, 1.0 = very dark edges
CHROMATIC_INTENSITY = 0.5      # Pixel offset for color split
SCANLINE_INTENSITY = 0.15       # 0.0 = invisible, 1.0 = very visible
BLOOM_THRESHOLD = 180           # Brightness level to start glowing (0-255)
BLOOM_INTENSITY = 0.3           # How strong the glow is
SHAKE_DURATION = 200            # Milliseconds
SHAKE_INTENSITY = 8             # Pixel radius of shake
SHAKE_ON_HIT = True            # Shake when player is hit
SHAKE_ON_OBSTACLE = True       # Shake when hitting obstacles
GROUND_TILE_SIZE = 256          # Size of each ground texture tile (pixels)
GROUND_TINT_COLOR = None        # (R, G, B) to tint the ground, None = no tint
ENEMY_DESPAWN_MS = 700  
PLAYER_PAUSE_ON_CATCH_MS = 800

PLACEMENT_ATTEMPTS_MULT = 30


def slice_row(sheet, row_index, frame_w, frame_h, frames_count=None):

    sheet_w, sheet_h = sheet.get_size()
    max_cols = sheet_w // frame_w
    if frames_count is None:
        frames_count = max_cols
    frames = []
    y = row_index * frame_h
    for i in range(frames_count):
        x = i * frame_w
        if x + frame_w <= sheet_w and y + frame_h <= sheet_h:
            frame = sheet.subsurface(pygame.Rect(x, y, frame_w, frame_h)).copy()
            frames.append(frame)
    return frames

def build_animations_from_master(path, frame_w, frame_h, layout, scale=1.0):
    # If the sprite sheet file doesn't exist, create placeholder animations
    if not os.path.isfile(path):
        fallback = pygame.Surface((frame_w, frame_h), pygame.SRCALPHA)
        fallback.fill((200, 100, 100, 255))
        anims = {}
        for st in ['idle', 'run', 'transition']:
            anims[st] = {}
            for f in ['down', 'left', 'right', 'up']:
                anims[st][f] = [fallback]
        return anims

    # Load the sprite sheet
    sheet = pygame.image.load(path).convert_alpha()
    anims = {}
    
    # Process each animation defined in the layout
    for entry in layout:
        row = entry['row']
        state = entry['state']
        facing = entry['facing']
        frames_count = entry.get('frames', None)
        
        frames = slice_row(sheet, row, frame_w, frame_h, frames_count)
        
        if scale != 1.0:
            frames = [pygame.transform.scale(f, (int(f.get_width()*scale), int(f.get_height()*scale))) for f in frames]
        
        if state not in anims:
            anims[state] = {}
        anims[state][facing] = frames
    
    for st in ['idle', 'run', 'transition']:
        if st not in anims:
            anims[st] = {}
        for dirn in ['down', 'left', 'right', 'up']:
            if dirn not in anims[st] or len(anims[st][dirn]) == 0:
                # Create a gray placeholder frame
                s = pygame.Surface((frame_w, frame_h), pygame.SRCALPHA)
                s.fill((150, 150, 150))
                anims[st][dirn] = [s]
    
    return anims

def facing_from_vector(vec):

    if vec.length_squared() == 0:
        return 'down'
    vx, vy = vec.x, vec.y
    if abs(vx) > abs(vy):
        return 'right' if vx > 0 else 'left'
    else:
        return 'down' if vy > 0 else 'up'

def lerp_color(c1, c2, t):

    r = int(c1[0] + (c2[0] - c1[0]) * t)
    g = int(c1[1] + (c2[1] - c1[1]) * t)
    b = int(c1[2] + (c2[2] - c1[2]) * t)
    return (r, g, b)

def get_sky_color(cycle_time, day_len, night_len):

    cycle_total = day_len + night_len
    t = cycle_time % cycle_total
    
    if t < day_len:
        day_progress = t / day_len
        
        if day_progress < 0.2:
            blend = day_progress / 0.2
            return lerp_color(SKY_COLORS['sunrise'], SKY_COLORS['afternoon'], blend)
        elif day_progress < 0.8:
            return SKY_COLORS['afternoon']
        else:
            blend = (day_progress - 0.8) / 0.2
            return lerp_color(SKY_COLORS['afternoon'], SKY_COLORS['sunset'], blend)
    else:
        night_progress = (t - day_len) / night_len
        
        if night_progress < 0.2:
            blend = night_progress / 0.2
            return lerp_color(SKY_COLORS['sunset'], SKY_COLORS['night'], blend)
        elif night_progress < 0.8:
            return SKY_COLORS['night']
        else:
            blend = (night_progress - 0.8) / 0.2
            return lerp_color(SKY_COLORS['night'], SKY_COLORS['sunrise'], blend)

# ===================== CUTSCENE SYSTEM =====================

class Cutscene:

    def __init__(self, text, font):
        self.full_text = text
        self.displayed_text = ""
        self.char_index = 0
        self.last_char_time = pygame.time.get_ticks()
        self.font = font
        self.finished = False
        self.can_skip = False
        self.skip_delay = 500  # Can skip after 500ms
        self.start_time = pygame.time.get_ticks()
        
    def update(self):

        now = pygame.time.get_ticks()
        
        if now - self.start_time > self.skip_delay:
            self.can_skip = True
        
        if self.char_index < len(self.full_text):
            if now - self.last_char_time >= CUTSCENE_TEXT_SPEED:
                self.displayed_text += self.full_text[self.char_index]
                self.char_index += 1
                self.last_char_time = now
        else:
            self.finished = True
    

        if self.can_skip:
            self.displayed_text = self.full_text
            self.char_index = len(self.full_text)
            self.finished = True
    
    def draw(self, screen, screen_size):
        """Draws the cutscene textbox"""
        box_width = screen_size[0] - 100
        box_height = 140
        box_x = 50
        box_y = screen_size[1] - box_height - 40
        
        box_surf = pygame.Surface((box_width, box_height), pygame.SRCALPHA)
        box_surf.fill(CUTSCENE_BG_COLOR)
        screen.blit(box_surf, (box_x, box_y))
        
        pygame.draw.rect(screen, CUTSCENE_BORDER_COLOR, (box_x, box_y, box_width, box_height), 4)
        
        words = self.displayed_text.split(' ')
        lines = []
        current_line = ""
        
        for word in words:
            test_line = current_line + word + " "
            test_surf = self.font.render(test_line, True, CUTSCENE_TEXT_COLOR)
            if test_surf.get_width() < box_width - 40:
                current_line = test_line
            else:
                if current_line:
                    lines.append(current_line)
                current_line = word + " "
        if current_line:
            lines.append(current_line)
        
        text_y = box_y + 20
        for line in lines:
            text_surf = self.font.render(line, True, CUTSCENE_TEXT_COLOR)
            screen.blit(text_surf, (box_x + 20, text_y))
            text_y += 30
        
        if self.finished:
            indicator_font = pygame.font.SysFont(None, 24)
            indicator = indicator_font.render("Press SPACE to continue...", True, (200, 200, 100))
            screen.blit(indicator, (box_x + box_width - indicator.get_width() - 20, box_y + box_height - 35))
        elif self.can_skip:
            skip_font = pygame.font.SysFont(None, 20)
            skip_text = skip_font.render("Press SPACE to skip", True, (150, 150, 150))
            screen.blit(skip_text, (box_x + box_width - skip_text.get_width() - 20, box_y + box_height - 30))

def draw_key_icon(screen, x, y, key_text, size=40):
    """Draws a keyboard key icon"""
    key_rect = pygame.Rect(x, y, size, size)
    pygame.draw.rect(screen, (60, 60, 80), key_rect, border_radius=5)
    pygame.draw.rect(screen, (100, 100, 120), key_rect, 3, border_radius=5)
    
    key_font = pygame.font.SysFont(None, 28, bold=True)
    text_surf = key_font.render(key_text, True, (220, 220, 240))
    text_rect = text_surf.get_rect(center=key_rect.center)
    screen.blit(text_surf, text_rect)

def create_intro_cutscene(screen, screen_size, font):
    """Creates the intro cutscene with WASD/Arrow keys display"""
    text = "Huh, these villagers think too much of themselves. Let's run away...  at least for now."
    return Cutscene(text, font)

def draw_control_hints(screen, screen_size):
    """Draws the control key hints during intro cutscene"""
    center_x = screen_size[0] // 2
    center_y = 180
    key_size = 45
    spacing = 10
    
    # Draw "Move with:" text
    hint_font = pygame.font.SysFont(None, 32)
    hint_text = hint_font.render("Move with:", True, (255, 255, 255))
    screen.blit(hint_text, (center_x - hint_text.get_width() // 2, center_y - 100))
    
    # WASD keys
    wasd_y = center_y
    draw_key_icon(screen, center_x - key_size // 2, wasd_y - key_size - spacing, "W", key_size)
    draw_key_icon(screen, center_x - key_size - spacing - key_size // 2, wasd_y, "A", key_size)
    draw_key_icon(screen, center_x - key_size // 2, wasd_y, "S", key_size)
    draw_key_icon(screen, center_x + spacing + key_size // 2, wasd_y, "D", key_size)
    
    # "or" text
    or_text = hint_font.render("SHIFT TO RUN", True, (200, 200, 200))
    screen.blit(or_text, (center_x - or_text.get_width() // 2, wasd_y + key_size + 20))
    


def create_night_cutscene(font):
    text = "Hahahaha... trying to hunt me down just because I have another side? Well, who doesn't! look at you!"
    return Cutscene(text, font)


class AudioManager:

    def __init__(self):
        pygame.mixer.init()
        self.sounds = {}
        self.current_music = None
        self.movement_channel = None  # Dedicated channel for movement sounds
        
    def load_sound(self, name, path, volume=1.0):
        """Load a sound effect"""
        if os.path.isfile(path):
            try:
                sound = pygame.mixer.Sound(path)
                sound.set_volume(volume * MASTER_SFX_VOLUME)
                self.sounds[name] = sound
                return True
            except Exception as e:
                print(f"Failed to load sound {name}: {e}")
                return False
        return False
    
    def play_sound(self, name, loops=0):

        if name in self.sounds:
            self.sounds[name].play(loops=loops)
    
    def stop_sound(self, name):

        if name in self.sounds:
            self.sounds[name].stop()
    
    def play_movement_sound(self, sound_name):

        if sound_name in self.sounds:
            if self.movement_channel is None or not self.movement_channel.get_busy():
                self.movement_channel = self.sounds[sound_name].play(loops=-1)
    
    def stop_movement_sounds(self):

        if self.movement_channel and self.movement_channel.get_busy():
            self.movement_channel.stop()
    
    def play_music(self, path, volume=1.0, loops=-1):

        if self.current_music == path and pygame.mixer.music.get_busy():
            return  # Already playing this track
        
        if os.path.isfile(path):
            try:
                pygame.mixer.music.load(path)
                pygame.mixer.music.set_volume(volume * MASTER_MUSIC_VOLUME)
                pygame.mixer.music.play(loops=loops)
                self.current_music = path
            except Exception as e:
                print(f"Failed to load music {path}: {e}")
    
    def stop_music(self):
        pygame.mixer.music.stop()
        self.current_music = None
    
    def fade_out_music(self, ms=1000):
        pygame.mixer.music.fadeout(ms)

# ===================== SHADER/VISUAL EFFECTS =====================

class ShaderEffect:
    def __init__(self, screen_size):
        self.screen_w, self.screen_h = screen_size
        self.vignette_surf = self._create_vignette() if ENABLE_VIGNETTE else None
        self.scanline_surf = self._create_scanlines() if ENABLE_SCANLINES else None
    
    def _create_vignette(self):
        surf = pygame.Surface((self.screen_w, self.screen_h), pygame.SRCALPHA)
        center_x, center_y = self.screen_w // 2, self.screen_h // 2
        max_dist = math.hypot(center_x, center_y)
        
        for y in range(0, self.screen_h, 2):  # Step by 2 for performance
            for x in range(0, self.screen_w, 2):
                dist = math.hypot(x - center_x, y - center_y)
                alpha = int(255 * (dist / max_dist) * VIGNETTE_INTENSITY)
                pygame.draw.rect(surf, (0, 0, 0, alpha), (x, y, 2, 2))
        
        return surf
    
    def _create_scanlines(self):
        surf = pygame.Surface((self.screen_w, self.screen_h), pygame.SRCALPHA)
        alpha = int(255 * SCANLINE_INTENSITY)
        
        for y in range(0, self.screen_h, 2):
            pygame.draw.line(surf, (0, 0, 0, alpha), (0, y), (self.screen_w, y))
        
        return surf
    
    def apply_chromatic_aberration(self, screen):
        if not ENABLE_CHROMATIC_ABERRATION or CHROMATIC_INTENSITY <= 0:
            return
        
        temp = screen.copy()
        offset = int(CHROMATIC_INTENSITY)
        
        # Red channel shifted left
        red_surf = pygame.Surface((self.screen_w, self.screen_h))
        red_surf.blit(temp, (-offset, 0))
        red_surf.set_colorkey((0, 0, 0))
        
        blue_surf = pygame.Surface((self.screen_w, self.screen_h))
        blue_surf.blit(temp, (offset, 0))
        blue_surf.set_colorkey((0, 0, 0))
        
        # Apply channels with blend modes
        screen.blit(red_surf, (0, 0), special_flags=pygame.BLEND_RGB_ADD)
        screen.blit(blue_surf, (0, 0), special_flags=pygame.BLEND_RGB_ADD)
    
    def apply_bloom(self, screen):
        if not ENABLE_BLOOM:
            return
        
        small_w, small_h = self.screen_w // 4, self.screen_h // 4
        bloom_surf = pygame.transform.smoothscale(screen, (small_w, small_h))
        
        bloom_pixels = pygame.surfarray.pixels3d(bloom_surf)
        mask = (bloom_pixels[:,:,0] + bloom_pixels[:,:,1] + bloom_pixels[:,:,2]) / 3 > BLOOM_THRESHOLD
        bloom_pixels[:,:,0] = bloom_pixels[:,:,0] * mask
        bloom_pixels[:,:,1] = bloom_pixels[:,:,1] * mask
        bloom_pixels[:,:,2] = bloom_pixels[:,:,2] * mask
        del bloom_pixels  # Release the pixel lock
        
        bloom_surf = pygame.transform.smoothscale(bloom_surf, (self.screen_w, self.screen_h))
        bloom_surf.set_alpha(int(255 * BLOOM_INTENSITY))
        
        screen.blit(bloom_surf, (0, 0), special_flags=pygame.BLEND_RGB_ADD)
    
    def apply_effects(self, screen):
        if ENABLE_CHROMATIC_ABERRATION:
            self.apply_chromatic_aberration(screen)
        
        if ENABLE_BLOOM:
            self.apply_bloom(screen)
        
        if ENABLE_VIGNETTE and self.vignette_surf:
            screen.blit(self.vignette_surf, (0, 0))
        
        if ENABLE_SCANLINES and self.scanline_surf:
            screen.blit(self.scanline_surf, (0, 0))


class GroundRenderer:
    def __init__(self, texture_path, world_size, tile_size=GROUND_TILE_SIZE):
        self.world_w, self.world_h = world_size
        self.tile_size = tile_size
        self.texture = self._load_texture(texture_path)
        self.tint = GROUND_TINT_COLOR
        
    def _load_texture(self, path):
        if os.path.isfile(path):
            try:
                texture = pygame.image.load(path).convert()
                # Scale texture to tile size
                texture = pygame.transform.scale(texture, (self.tile_size, self.tile_size))
                
                # Apply tint if specified
                if GROUND_TINT_COLOR:
                    tint_surf = pygame.Surface((self.tile_size, self.tile_size))
                    tint_surf.fill(GROUND_TINT_COLOR)
                    texture.blit(tint_surf, (0, 0), special_flags=pygame.BLEND_MULT)
                
                return texture
            except Exception as e:
                print(f"Failed to load ground texture: {e}")
                return self._create_fallback_texture()
        else:
            print(f"Ground texture not found at {path}, using fallback")
            return self._create_fallback_texture()
    
    def _create_fallback_texture(self):
        texture = pygame.Surface((self.tile_size, self.tile_size))
        texture.fill((50, 120, 50))
        
        for _ in range(100):
            x = random.randint(0, self.tile_size - 1)
            y = random.randint(0, self.tile_size - 1)
            shade = random.randint(-20, 20)
            color = (
                max(0, min(255, 50 + shade)),
                max(0, min(255, 120 + shade)),
                max(0, min(255, 50 + shade))
            )
            pygame.draw.circle(texture, color, (x, y), random.randint(1, 3))
        
        return texture
    
    def draw(self, screen, camera_offset):
        start_tile_x = max(0, int(camera_offset.x) // self.tile_size)
        start_tile_y = max(0, int(camera_offset.y) // self.tile_size)
        
        tiles_x = (screen.get_width() // self.tile_size) + 2
        tiles_y = (screen.get_height() // self.tile_size) + 2
        
        end_tile_x = min(start_tile_x + tiles_x, (self.world_w // self.tile_size) + 1)
        end_tile_y = min(start_tile_y + tiles_y, (self.world_h // self.tile_size) + 1)
        
        for ty in range(start_tile_y, end_tile_y):
            for tx in range(start_tile_x, end_tile_x):
                world_x = tx * self.tile_size
                world_y = ty * self.tile_size
                screen_x = world_x - int(camera_offset.x)
                screen_y = world_y - int(camera_offset.y)
                
                screen.blit(self.texture, (screen_x, screen_y))

# ===================== GAME CLASSES =====================

class Camera:
    def __init__(self, screen_size, world_size):
        self.screen_w, self.screen_h = screen_size
        self.world_w, self.world_h = world_size
        self.offset = Vector2(0, 0)
        self.target_offset = Vector2(0, 0)
        self.shake_offset = Vector2(0, 0)
        self.shake_until = 0
        self.shake_intensity = 0
    
    def update(self, target_rect, target_velocity=None):
        target_x = target_rect.centerx - self.screen_w // 2
        target_y = target_rect.centery - self.screen_h // 2
        
        if target_velocity and CAMERA_LOOKAHEAD > 0:
            if target_velocity.length_squared() > 100:  # Only if moving significantly
                look_dir = target_velocity.normalize()
                target_x += look_dir.x * CAMERA_LOOKAHEAD
                target_y += look_dir.y * CAMERA_LOOKAHEAD
        
        target_x = max(0, min(target_x, self.world_w - self.screen_w))
        target_y = max(0, min(target_y, self.world_h - self.screen_h))
        
        self.target_offset.x = target_x
        self.target_offset.y = target_y
        
        self.offset.x += (self.target_offset.x - self.offset.x) * CAMERA_SMOOTHING
        self.offset.y += (self.target_offset.y - self.offset.y) * CAMERA_SMOOTHING
        
        now = pygame.time.get_ticks()
        if ENABLE_CAMERA_SHAKE and now < self.shake_until:
            progress = 1.0 - (self.shake_until - now) / SHAKE_DURATION
            intensity = self.shake_intensity * (1.0 - progress)  # Fade out
            self.shake_offset.x = random.uniform(-intensity, intensity)
            self.shake_offset.y = random.uniform(-intensity, intensity)
        else:
            self.shake_offset.x = 0
            self.shake_offset.y = 0
    
    def apply(self, rect):
        return rect.move(
            -int(self.offset.x + self.shake_offset.x), 
            -int(self.offset.y + self.shake_offset.y)
        )
    
    def shake(self, intensity=SHAKE_INTENSITY, duration=SHAKE_DURATION):
        if ENABLE_CAMERA_SHAKE:
            self.shake_intensity = intensity
            self.shake_until = pygame.time.get_ticks() + duration

class Obstacle(pygame.sprite.Sprite):
    def __init__(self, base_image, top_image, pos):
        super().__init__()
        self.base_image = base_image
        self.top_image = top_image
        self.rect = self.base_image.get_rect(center=pos)
        self.collision_mask = pygame.mask.from_surface(self.base_image)
        self.collision_rect = self.base_image.get_rect(center=pos)
        self.top_rect = self.top_image.get_rect(center=pos) if self.top_image else None

class Player(pygame.sprite.Sprite):

    def __init__(self, animations, pos, frame_durations=None, audio_manager=None):
        super().__init__()
        self.anim = animations
        self.state = 'idle'
        self.facing = 'down'
        self.frame_idx = 0
        self.frame_durations = frame_durations or FRAME_DURATION
        self.last_frame_time = pygame.time.get_ticks()
        self.audio = audio_manager
        
        self.current_frames = self.anim[self.state][self.facing]
        self.image = self.current_frames[self.frame_idx]
        self.rect = self.image.get_rect(center=pos)
        self.mask = pygame.mask.from_surface(self.image)
        
        # Physics
        self.pos = Vector2(pos)
        self.vel = Vector2(0, 0)
        self.acc = Vector2(0, 0)
        
        # Stats
        self.stamina = STAMINA_MAX
        self.hearts = PLAYER_MAX_HEARTS
        
        # Status effects
        self.flash_until = 0  #
        self.freeze_until = 0  # 
        self.pause_until = 0   #
        
        self.playing_night_animation = False
        
        self.is_moving = False
        self.is_sprinting = False

    def play_transition_animation(self):
        self.playing_night_animation = True
        self.state = 'transition'
        self.frame_idx = 0
        self.last_frame_time = pygame.time.get_ticks()
        self.current_frames = self.anim[self.state][self.facing]
        self.image = self.current_frames[self.frame_idx]
        self.mask = pygame.mask.from_surface(self.image)
        
        self.pause_until = pygame.time.get_ticks() + TRANSITION_MS
        
        if self.audio:
            self.audio.play_sound('howl')

    def stop_night_animation(self):
        self.playing_night_animation = False
        self.state = 'idle'
        self.frame_idx = 0
        self.last_frame_time = pygame.time.get_ticks()

    def update(self, dt, keys, allow_control=True):
        now_ms = pygame.time.get_ticks()
        
        if now_ms < self.pause_until:
            self.vel *= 0.9
            self.pos += self.vel * dt
            self.rect.center = (int(self.pos.x), int(self.pos.y))
            self._update_animation()
            # Stop movement sounds when paused
            if self.audio:
                self.audio.stop_movement_sounds()
            self.is_moving = False
            self.is_sprinting = False
            return
        
        if now_ms < self.freeze_until:
            self.vel *= 0.9
            self.pos += self.vel * dt
            self.rect.center = (int(self.pos.x), int(self.pos.y))
            self._update_animation()
            if self.audio:
                self.audio.stop_movement_sounds()
            self.is_moving = False
            self.is_sprinting = False
            return
        
        if self.playing_night_animation and now_ms >= self.pause_until:
            self.stop_night_animation()
        
        if not self.playing_night_animation:
            sprinting = (keys[pygame.K_LSHIFT] or keys[pygame.K_RSHIFT]) and self.stamina > STAMINA_MIN_TO_SPRINT and allow_control
            move = Vector2(0, 0)
            
            if allow_control:
                if keys[pygame.K_w] or keys[pygame.K_UP]: move.y = -1
                if keys[pygame.K_s] or keys[pygame.K_DOWN]: move.y = 1
                if keys[pygame.K_a] or keys[pygame.K_LEFT]: move.x = -1
                if keys[pygame.K_d] or keys[pygame.K_RIGHT]: move.x = 1
            
            speed_cap = MAX_SPEED * (SPRINT_MULTIPLIER if sprinting else 1.0)
            
            is_currently_moving = move.length_squared() > 0
            
            if is_currently_moving:
                move = move.normalize()
                desired = move * speed_cap
                change = desired - self.vel
                max_change = ACCELERATION * dt
                if change.length() > max_change:
                    change = change.normalize() * max_change
                self.vel += change
            else:
                # Apply friction when not moving
                if self.vel.length_squared() > 0:
                    decel = FRICTION * dt
                    if self.vel.length() <= decel:
                        self.vel = Vector2(0, 0)
                    else:
                        self.vel -= self.vel.normalize() * decel
            
            if self.vel.length() > speed_cap:
                self.vel.scale_to_length(speed_cap)
            
            self.pos += self.vel * dt
            self.pos.x = max(0, min(self.pos.x, WORLD_SIZE[0]))
            self.pos.y = max(0, min(self.pos.y, WORLD_SIZE[1]))
            self.rect.center = (int(self.pos.x), int(self.pos.y))
            
            if self.vel.length_squared() > 10:
                self.state = 'run'
                self.facing = facing_from_vector(self.vel)
            else:
                self.state = 'idle'
            
            if self.audio:
                if is_currently_moving and self.vel.length() > 10:
                    if sprinting and not self.is_sprinting:
                        # Switched to sprinting
                        self.audio.stop_movement_sounds()
                        self.audio.play_movement_sound('running')
                        self.is_sprinting = True
                        self.is_moving = True
                    elif not sprinting and (self.is_sprinting or not self.is_moving):
                        # Switched to walking or just started moving
                        self.audio.stop_movement_sounds()
                        self.audio.play_movement_sound('walking')
                        self.is_sprinting = False
                        self.is_moving = True
                else:
                    # Stopped moving
                    if self.is_moving:
                        self.audio.stop_movement_sounds()
                        self.is_moving = False
                        self.is_sprinting = False
            
            # Update stamina
            if sprinting and move.length_squared() > 0:
                self.stamina -= STAMINA_DRAIN_PER_SEC * dt
                self.stamina = max(0.0, self.stamina)
            else:
                self.stamina += STAMINA_RECOVER_PER_SEC * dt
                self.stamina = min(STAMINA_MAX, self.stamina)
        
        self._update_animation()

    def _update_animation(self):
        now = pygame.time.get_ticks()
        
        # Get current animation frames
        self.current_frames = self.anim[self.state].get(self.facing, self.anim[self.state]['down'])
        
        # Calculate frame duration (faster when moving fast)
        base_duration = self.frame_durations.get(self.state, 100)
        
        if self.state == 'run':
            # Make run animation speed match movement speed
            speed = self.vel.length()
            max_possible = MAX_SPEED * SPRINT_MULTIPLIER
            speed_ratio = min(1.0, speed / max_possible)
            scale = 1.4 - 0.8 * speed_ratio
            duration = max(25, int(base_duration * scale))
        else:
            duration = base_duration
        
        # Check if it's time for next frame
        if now - self.last_frame_time >= duration:
            self.frame_idx = (self.frame_idx + 1) % len(self.current_frames)
            self.last_frame_time = now
            self.image = self.current_frames[self.frame_idx]
            self.mask = pygame.mask.from_surface(self.image)

    def collide_with_obstacle(self, obstacle):
        dir_vec = (self.pos - Vector2(obstacle.collision_rect.center))
        if dir_vec.length_squared() == 0:
            dir_vec = Vector2(random.uniform(-1, 1), random.uniform(-1, 1))
        dir_vec = dir_vec.normalize()
        self.vel = dir_vec * KNOCKBACK_SPEED
        self.freeze_until = pygame.time.get_ticks() + 500
        
        # Play pushback sound
        if self.audio:
            self.audio.play_sound('pushback')
        
        return True  # Signal that collision occurred

    def hit_by_enemy(self, enemy):
        dir_vec = (self.pos - Vector2(enemy.rect.center))
        if dir_vec.length_squared() == 0:
            dir_vec = Vector2(random.uniform(-1, 1), random.uniform(-1, 1))
        dir_vec = dir_vec.normalize()
        self.vel = dir_vec * KNOCKBACK_SPEED
        self.flash_until = pygame.time.get_ticks() + HIT_FLASH_MS
        
        # Play hurt sound
        if self.audio:
            self.audio.play_sound('hurt')
        
        return True  # Signal that hit occurred
    
    def gain_heart(self):
        if self.audio:
            self.audio.play_sound('heal')

# ===================== NAVIGATION & PATHFINDING =====================

def build_nav_grid(world_size, cell_size, obstacles, expand_cells=1):
    cols = math.ceil(world_size[0] / cell_size)
    rows = math.ceil(world_size[1] / cell_size)
    grid = [[0 for _ in range(cols)] for _ in range(rows)]
    
    for ob in obstacles:
        r = ob.collision_rect
        left = max(0, r.left // cell_size)
        right = min(cols-1, r.right // cell_size)
        top = max(0, r.top // cell_size)
        bottom = min(rows-1, r.bottom // cell_size)
        
        for cy in range(max(0, top - expand_cells), min(rows, bottom + 1 + expand_cells)):
            for cx in range(max(0, left - expand_cells), min(cols, right + 1 + expand_cells)):
                grid[cy][cx] = 1
    
    return grid

def world_to_cell(pos, cell_size):
    cx = int(pos.x // cell_size)
    cy = int(pos.y // cell_size)
    return cx, cy

def cell_to_world_center(cx, cy, cell_size):
    x = cx * cell_size + cell_size // 2
    y = cy * cell_size + cell_size // 2
    return Vector2(x, y)

def neighbors_for(cx, cy, grid):
    rows = len(grid)
    cols = len(grid[0])
    nbrs = []
    
    for dy in (-1, 0, 1):
        for dx in (-1, 0, 1):
            if dx == 0 and dy == 0:
                continue
            nx = cx + dx
            ny = cy + dy
            if 0 <= nx < cols and 0 <= ny < rows and grid[ny][nx] == 0:
                # Diagonal moves cost more
                cost = math.hypot(dx, dy)
                nbrs.append((nx, ny, cost))
    
    return nbrs

def heuristic(a, b):
    (ax, ay) = a
    (bx, by) = b
    return math.hypot(bx - ax, by - ay)

def a_star(grid, start, goal, max_nodes=25000):
    if start == goal:
        return [start]
    
    rows = len(grid)
    cols = len(grid[0])
    sx, sy = start
    gx, gy = goal
    
    # Validate start and goal
    if not (0 <= sx < cols and 0 <= sy < rows):
        return None
    if not (0 <= gx < cols and 0 <= gy < rows):
        return None
    if grid[sy][sx] == 1 or grid[gy][gx] == 1:
        return None
    
    # A* algorithm
    open_heap = []
    heapq.heappush(open_heap, (0 + heuristic(start, goal), 0, start))
    came_from = {}
    gscore = {start: 0}
    visited = 0
    
    while open_heap:
        f, g, current = heapq.heappop(open_heap)
        visited += 1
        
        if visited > max_nodes:
            return None  # Path too complex
        
        if current == goal:
            path = [current]
            while current in came_from:
                current = came_from[current]
                path.append(current)
            path.reverse()
            return path
        
        cx, cy = current
        for nx, ny, cost in neighbors_for(cx, cy, grid):
            neigh = (nx, ny)
            tentative_g = gscore[current] + cost
            
            if neigh not in gscore or tentative_g < gscore[neigh]:
                came_from[neigh] = current
                gscore[neigh] = tentative_g
                fscore = tentative_g + heuristic(neigh, goal)
                heapq.heappush(open_heap, (fscore, tentative_g, neigh))
    
    return None

# ===================== ENEMY CLASS =====================

class Enemy(pygame.sprite.Sprite):
    def __init__(self, pos, nav_grid, cell_size, anims, frame_durations):
        super().__init__()
        self.anims = anims
        self.frame_durations = frame_durations or FRAME_DURATION
        self.state = 'idle'
        self.facing = 'down'
        self.frame_idx = 0
        self.last_frame_time = pygame.time.get_ticks()
        
        self.current_frames = self.anims[self.state][self.facing]
        self.image = self.current_frames[self.frame_idx]
        self.rect = self.image.get_rect(center=pos)
        self.mask = pygame.mask.from_surface(self.image)
        
        self.pos = Vector2(pos)
        self.vel = Vector2(0, 0)
        
        self.nav_grid = nav_grid
        self.cell_size = cell_size
        self.path = []
        self.path_cells = []
        self.path_idx = 0
        self.last_recalc = -9999.0
        self.recalc_interval = PATH_RECALC_INTERVAL
        self.last_player_cell = None
        
        self.mode = 'chase'  # 'chase', 'flee', or 'halt'
        self.hit = False
        self.hit_time = 0

    def request_path_to(self, player_pos, current_time):
        pcx, pcy = world_to_cell(player_pos, self.cell_size)
        scx, scy = world_to_cell(self.pos, self.cell_size)
        now = current_time
        
        if (now - self.last_recalc) < self.recalc_interval:
            return
        
        self.last_recalc = now
        rows = len(self.nav_grid)
        cols = len(self.nav_grid[0])
        
        # Choose goal based on mode
        if self.mode == 'chase':
            # Go toward player
            goal = (pcx, pcy)
        elif self.mode == 'flee':
            # Run away from player
            gx = scx + (scx - pcx)
            gy = scy + (scy - pcy)
            gx = max(0, min(cols-1, gx))
            gy = max(0, min(rows-1, gy))
            goal = (gx, gy)
            
            # If flee target is blocked, try corners
            if self.nav_grid[goal[1]][goal[0]] == 1:
                corners = [(0, 0), (cols-1, 0), (0, rows-1), (cols-1, rows-1)]
                best = None
                best_d = -1
                for c in corners:
                    cx, cy = c
                    if self.nav_grid[cy][cx] == 0:
                        d = math.hypot(cx - pcx, cy - pcy)
                        if d > best_d:
                            best_d = d
                            best = c
                if best:
                    goal = best
        else:
            return  # No pathfinding in halt mode
        
        path_cells = a_star(self.nav_grid, (scx, scy), goal)
        if not path_cells:
            self.path = []
            self.path_idx = 0
            return
        
        world_path = [cell_to_world_center(cx, cy, self.cell_size) for (cx, cy) in path_cells]
        
        compressed = []
        for i, pt in enumerate(world_path):
            if i == 0 or i == len(world_path)-1:
                compressed.append(pt)
                continue
            prev = world_path[i-1]
            nxt = world_path[i+1]
            dir1 = (pt - prev)
            dir2 = (nxt - pt)
            if dir1.length_squared() == 0 or dir2.length_squared() == 0:
                compressed.append(pt)
                continue
            dir1 = dir1.normalize()
            dir2 = dir2.normalize()
            if dir1.dot(dir2) < 0.999:
                compressed.append(pt)
        
        self.path = compressed
        self.path_idx = 0

    def update_animation(self):
        now = pygame.time.get_ticks()
        speed = self.vel.length()
        
        prev_state = self.state
        self.state = 'run' if speed > 4.0 else 'idle'
        
        if speed > 4.0:
            self.facing = facing_from_vector(self.vel)
        
        self.current_frames = self.anims[self.state].get(self.facing, self.anims[self.state]['down'])
        
        base = self.frame_durations.get(self.state, 120)
        ratio = min(1.0, speed / ENEMY_MAX_SPEED)
        scale = 1.2 - 0.9 * ratio
        dur = max(30, int(base * scale))
        
        # Update frame
        if now - self.last_frame_time >= dur:
            self.frame_idx = (self.frame_idx + 1) % len(self.current_frames)
            self.last_frame_time = now
            self.image = self.current_frames[self.frame_idx]
            self.mask = pygame.mask.from_surface(self.image)

    def update(self, dt, player, obstacles_group, all_enemies, current_time):
        if self.hit:
            return  # Don't move if caught
        
        # Get path to/from player
        self.request_path_to(player.pos, current_time)
        
        sep = Vector2(0, 0)
        for other in all_enemies:
            if other is self:
                continue
            d = self.pos.distance_to(other.pos)
            if d < SEPARATION_RADIUS and d > 0:
                away = (self.pos - other.pos) / (d * d)
                sep += away
        if sep.length_squared() > 0:
            sep = sep.normalize() * (SEPARATION_FORCE * dt)
        
        avoid = Vector2(0, 0)
        avoid_radius = max(self.cell_size * 0.8, 32)
        avoid_force = 600.0
        for ob in obstacles_group:
            ob_center = Vector2(ob.collision_rect.center)
            d = self.pos.distance_to(ob_center)
            if d < avoid_radius and d > 0:
                repulse = (self.pos - ob_center) / (d * d)
                avoid += repulse
        if avoid.length_squared() > 0:
            avoid = avoid.normalize() * (avoid_force * dt)

        # Path-following / behavior-based desired velocity
        target_vel = Vector2(0, 0)
        if self.path and self.path_idx < len(self.path):
            target = self.path[self.path_idx]
            if self.pos.distance_to(target) < max(10.0, self.cell_size * 0.35):
                self.path_idx += 1
            else:
                desired = (target - self.pos)
                if desired.length_squared() > 0:
                    target_vel = desired.normalize() * ENEMY_MAX_SPEED
        else:
            if self.mode == 'chase':
                desired = (player.pos - self.pos)
                if desired.length_squared() > 0:
                    target_vel = desired.normalize() * ENEMY_MAX_SPEED
            elif self.mode == 'flee':
                desired = (self.pos - player.pos)
                if desired.length_squared() > 0:
                    target_vel = desired.normalize() * ENEMY_MAX_SPEED

        steer = target_vel - self.vel
        steer += sep
        steer += avoid

        max_change = ENEMY_ACCELERATION * dt
        if steer.length() > max_change:
            steer = steer.normalize() * max_change
        self.vel += steer
        if self.vel.length() > ENEMY_MAX_SPEED:
            self.vel.scale_to_length(ENEMY_MAX_SPEED)

        next_pos = self.pos + self.vel * dt
        next_rect = self.rect.copy()
        next_rect.center = (int(next_pos.x), int(next_pos.y))
        collided = False
        for ob in obstacles_group:
            if next_rect.colliderect(ob.collision_rect):
                off = (ob.collision_rect.left - next_rect.left, ob.collision_rect.top - next_rect.top)
                if self.mask.overlap(ob.collision_mask, off):
                    # Slide away gently
                    push = (self.pos - Vector2(ob.collision_rect.center))
                    if push.length_squared() == 0:
                        push = Vector2(random.uniform(-1, 1), random.uniform(-1, 1))
                    push = push.normalize() * (self.cell_size * 0.06)
                    self.pos += push
                    self.vel *= 0.55
                    collided = True
                    # invalidate path so A* recomputes next tick
                    self.path = []
                    break

        if not collided:
            self.pos = next_pos

        self.rect.center = (int(self.pos.x), int(self.pos.y))
        self.update_animation()


# ------------------------------ placement utils ------------------------------

def place_obstacles(count, avoid_pos, min_dist, world_size, asset_pairs):
    obstacles = pygame.sprite.Group()
    attempts = 0
    placed = 0
    max_attempts = count * PLACEMENT_ATTEMPTS_MULT
    while placed < count and attempts < max_attempts:
        attempts += 1
        x = random.randint(64, world_size[0] - 64)
        y = random.randint(64, world_size[1] - 64)
        pos = Vector2(x, y)
        if pos.distance_to(Vector2(avoid_pos)) < min_dist:
            continue
        base_surf, top_surf = random.choice(asset_pairs)
        ob = Obstacle(base_surf, top_surf, pos)
        collide = False
        for e in obstacles:
            if ob.rect.colliderect(e.rect):
                collide = True
                break
        if collide:
            continue
        obstacles.add(ob)
        placed += 1
    return obstacles


def place_enemies(count, avoid_pos, min_dist, world_size, nav_grid, cell_size, enemy_anims_list):
    enemies = pygame.sprite.Group()
    attempts = 0
    placed = 0
    max_attempts = count * PLACEMENT_ATTEMPTS_MULT
    while placed < count and attempts < max_attempts:
        attempts += 1
        x = random.randint(64, world_size[0] - 64)
        y = random.randint(64, world_size[1] - 64)
        pos = Vector2(x, y)
        if pos.distance_to(Vector2(avoid_pos)) < min_dist:
            continue
        too_close = False
        for en in enemies:
            if pos.distance_to(Vector2(en.rect.center)) < 70:
                too_close = True
                break
        if too_close:
            continue
        anims = random.choice(enemy_anims_list)
        en = Enemy(pos, nav_grid, cell_size, anims, FRAME_DURATION)
        enemies.add(en)
        placed += 1
    return enemies



def main():
    pygame.init()
    screen = pygame.display.set_mode(SCREEN_SIZE)
    pygame.display.set_caption('Top-down: Day/Night with Sky Gradient')
    clock = pygame.time.Clock()
    
    # Initialize audio system
    audio = AudioManager()
    
    # Load sound effects
    audio.load_sound('walking', SFX_WALKING, SFX_VOLUME['walking'])
    audio.load_sound('running', SFX_RUNNING, SFX_VOLUME['running'])
    audio.load_sound('hurt', SFX_HURT, SFX_VOLUME['hurt'])
    audio.load_sound('heal', SFX_HEAL, SFX_VOLUME['heal'])
    audio.load_sound('howl', SFX_HOWL, SFX_VOLUME['howl'])
    audio.load_sound('pushback', SFX_PUSHBACK, SFX_VOLUME['pushback'])
    audio.load_sound('rip', SFX_RIP, SFX_VOLUME['rip'])

    def load_image(path, fallback_size=(48, 48)):
        if path and os.path.isfile(path):
            try:
                return pygame.image.load(path).convert_alpha()
            except Exception as e:
                print(f"Failed loading {path}: {e}")
        surf = pygame.Surface(fallback_size, pygame.SRCALPHA)
        surf.fill((180, 180, 180, 255))
        pygame.draw.rect(surf, (0, 0, 0), surf.get_rect(), 2)
        return surf

    player_anims = build_animations_from_master(MASTER_SHEET, FRAME_WIDTH, FRAME_HEIGHT, PLAYER_SHEET_LAYOUT, scale=SHEET_SCALE)
    
    player_night_path = os.path.join(ASSET_DIR, 'player', 'player_night.png')
    player_night_anims = build_animations_from_master(player_night_path, 48, FRAME_HEIGHT, PLAYER_NIGHT_LAYOUT, scale=SHEET_SCALE)

    trans_path = os.path.join(ASSET_DIR, 'player', 'ntransition.png')
    trans_anims = build_animations_from_master(trans_path, FRAME_WIDTH, FRAME_HEIGHT, PLAYER_TRANSITION_LAYOUT, scale=SHEET_SCALE)

    player_start = (WORLD_SIZE[0] // 2, WORLD_SIZE[1] // 2)
    
    player_day_anims = {state: {facing: frames[:] for facing, frames in dirs.items()} for state, dirs in player_anims.items()}
    
    player = Player(player_day_anims, player_start, frame_durations=FRAME_DURATION, audio_manager=audio)
    camera = Camera(SCREEN_SIZE, WORLD_SIZE)
    shader = ShaderEffect(SCREEN_SIZE)
    ground = GroundRenderer(GROUND_TEXTURE, WORLD_SIZE)

    # load obstacles
    tree_base = load_image(os.path.join(ASSET_DIR, 'obstacles', 'treebase.png'))
    tree_top = load_image(os.path.join(ASSET_DIR, 'obstacles', 'treetop.png'))
    rock_base = load_image(os.path.join(ASSET_DIR, 'obstacles', 'rock.png'))
    barrel_base = load_image(os.path.join(ASSET_DIR, 'obstacles', 'barrel.png'))
    barrel_top=None

    box1_base=load_image(os.path.join(ASSET_DIR, 'obstacles', 'box1.png'))
    box2_base=load_image(os.path.join(ASSET_DIR, 'obstacles', 'box2.png'))
    mkst_base=load_image(os.path.join(ASSET_DIR, 'obstacles', 'mkst.png'))
    pray_base=load_image(os.path.join(ASSET_DIR, 'obstacles', 'pray_bottom.png'))
    pray_top=load_image(os.path.join(ASSET_DIR, 'obstacles', 'pray_top.png'))

    box1,box2,mkst=None,None,None
    rock_top = None

    OBSTACLE_ASSET_PAIRS = [(tree_base, tree_top), (rock_base, rock_top),(box1_base,box1),(box2_base,box2),(mkst_base,mkst),(pray_base,pray_top)]
    obstacles = place_obstacles(OBSTACLE_COUNT, player_start, OBSTACLE_MIN_DIST, WORLD_SIZE, OBSTACLE_ASSET_PAIRS)

    nav_grid = build_nav_grid(WORLD_SIZE, NAV_CELL_SIZE, obstacles, expand_cells=NAV_EXPAND_CELLS)

    enemy_anims_list = []
    if os.path.isdir(ENEMY_SPRITES_DIR):
        for f in os.listdir(ENEMY_SPRITES_DIR):
            if f.lower().endswith('.png'):
                path = os.path.join(ENEMY_SPRITES_DIR, f)
                anims = build_animations_from_master(path, FRAME_WIDTH, FRAME_HEIGHT, ENEMY_SHEET_LAYOUT, scale=SHEET_SCALE)
                enemy_anims_list.append(anims)
    if not enemy_anims_list:
        surf = pygame.Surface((36, 36), pygame.SRCALPHA)
        pygame.draw.circle(surf, (160, 40, 40), (18, 18), 18)
        anims = {'idle': {}, 'run': {}}
        for d in ['down', 'left', 'right', 'up']:
            anims['idle'][d] = [surf]
            anims['run'][d] = [surf]
        enemy_anims_list.append(anims)

    enemies = place_enemies(ENEMY_COUNT, player_start, ENEMY_SPAWN_MIN_DIST, WORLD_SIZE, nav_grid, NAV_CELL_SIZE, enemy_anims_list)

    # heart UI
    heart_img = None
    if os.path.isfile(HEART_IMG):
        heart_img = load_image(HEART_IMG)
        if heart_img.get_height() > 48:
            scale = 24 / heart_img.get_height()
            heart_img = pygame.transform.scale(heart_img, (int(heart_img.get_width() * scale), 24))
    else:
        heart_img = pygame.Surface((36, 36), pygame.SRCALPHA)
        pygame.draw.polygon(heart_img, (220, 50, 50), [(18, 4), (30, 12), (18, 32), (6, 12)])
        pygame.draw.circle(heart_img, (220, 50, 50), (11, 10), 6)
        pygame.draw.circle(heart_img, (220, 50, 50), (25, 10), 6)

    menu_bg = load_image(MENU_BG, fallback_size=SCREEN_SIZE)
    win_img = load_image(WIN_IMG, fallback_size=SCREEN_SIZE)
    died_img = load_image(DIED_IMG, fallback_size=SCREEN_SIZE)
    start_btn_img = load_image(START_BTN_IMG, fallback_size=(160, 48))
    back_btn_img = load_image(BACK_BTN_IMG, fallback_size=(160, 48))

    font = pygame.font.SysFont(None, 28)

    # menu layout
    start_btn = pygame.Rect((SCREEN_SIZE[0] // 2 - start_btn_img.get_width() // 2 - 250, 
                             SCREEN_SIZE[1] // 2 + 100 , 
                             start_btn_img.get_width(), 
                             start_btn_img.get_height()))
    
    back_btn = pygame.Rect((SCREEN_SIZE[0] // 2 - back_btn_img.get_width() // 2, 
                           SCREEN_SIZE[1] // 2 + 100, 
                           back_btn_img.get_width(), 
                           back_btn_img.get_height()))

    # day/night state
    game_state = 'menu'  # 'menu', 'intro_cutscene', 'playing', 'night_cutscene', 'died', 'won'
    day_timer = 0.0
    is_night = False
    night_phase = 'none'  # 'none', 'idle_halt', 'flee'
    night_phase_timer = 0.0
    night_cutscene_shown = False  # Track if we've shown the night cutscene
    
    # Cutscene management
    current_cutscene = None

    last_player_pos_for_repath = Vector2(player.pos)
    
    # Start menu music
    audio.play_music(MUSIC_MENU, MUSIC_VOLUME['menu'], loops=-1)

    running = True
    while running:
        dt = clock.tick(FPS) / 1000.0
        now_ms = pygame.time.get_ticks()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                if game_state == 'menu':
                    running = False
                elif game_state in ['intro_cutscene', 'night_cutscene']:
                    pass  # Can't escape during cutscenes
                elif game_state in ['died', 'won']:
                    pass  # Can't escape from end screens
                else:
                    game_state = 'menu'
            elif event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
                if game_state == 'intro_cutscene' and current_cutscene:
                    if current_cutscene.finished:
                        game_state = 'playing'
                        current_cutscene = None
                        audio.play_music(MUSIC_DAY, MUSIC_VOLUME['day'], loops=-1)
                    else:
                        current_cutscene.skip()
                elif game_state == 'night_cutscene' and current_cutscene:
                    if current_cutscene.finished:
                        game_state = 'playing'
                        current_cutscene = None
                        night_phase = 'idle_halt'
                        night_phase_timer = TRANSITION_MS / 1000.0
                    else:
                        current_cutscene.skip()
            elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                mx, my = event.pos
                if game_state == 'menu':
                    if start_btn.collidepoint(mx, my):
                        player_fresh_anims = {state: {facing: frames[:] for facing, frames in dirs.items()} for state, dirs in player_anims.items()}
                        player = Player(player_fresh_anims, player_start, frame_durations=FRAME_DURATION, audio_manager=audio)
                        obstacles = place_obstacles(OBSTACLE_COUNT, player_start, OBSTACLE_MIN_DIST, WORLD_SIZE, OBSTACLE_ASSET_PAIRS)
                        nav_grid = build_nav_grid(WORLD_SIZE, NAV_CELL_SIZE, obstacles, expand_cells=NAV_EXPAND_CELLS)
                        enemies = place_enemies(ENEMY_COUNT, player_start, ENEMY_SPAWN_MIN_DIST, WORLD_SIZE, nav_grid, NAV_CELL_SIZE, enemy_anims_list)
                        day_timer = 0.0
                        is_night = False
                        night_phase = 'none'
                        night_phase_timer = 0.0
                        night_cutscene_shown = False
                        current_cutscene = create_intro_cutscene(screen, SCREEN_SIZE, font)
                        game_state = 'intro_cutscene'
                        audio.fade_out_music(500)
                elif game_state in ['won', 'died']:
                    if back_btn.collidepoint(mx, my):
                        game_state = 'menu'
                        # Play menu music
                        audio.play_music(MUSIC_MENU, MUSIC_VOLUME['menu'], loops=-1)

        keys = pygame.key.get_pressed()

        if game_state == 'menu':
            # draw menu
            screen.fill((30, 30, 30))
            screen.blit(menu_bg, (0, 0))
            screen.blit(start_btn_img, start_btn.topleft)
            pygame.display.flip()
            continue

        if game_state == 'intro_cutscene':
            # Draw the game world in background (frozen)
            sky_color = get_sky_color(day_timer, DAY_LENGTH, NIGHT_LENGTH)
            screen.fill(sky_color)
            
            # Draw ground texture
            ground.draw(screen, camera.offset)
            
            # Draw obstacles
            for ob in obstacles:
                screen.blit(ob.base_image, camera.apply(ob.collision_rect).topleft)
            
            # Draw enemies
            for en in sorted(enemies, key=lambda e: e.pos.y):
                screen.blit(en.image, camera.apply(en.rect).topleft)
            
            # Draw player
            screen.blit(player.image, camera.apply(player.rect).topleft)
            
            # Draw top parts
            for ob in obstacles:
                if ob.top_image:
                    screen.blit(ob.top_image, camera.apply(ob.top_rect).topleft)
            
            # Draw darkening overlay
            overlay = pygame.Surface(SCREEN_SIZE, pygame.SRCALPHA)
            overlay.fill((0, 0, 0, 120))
            screen.blit(overlay, (0, 0))
            
            # Draw control hints
            draw_control_hints(screen, SCREEN_SIZE)
            
            # Update and draw cutscene
            current_cutscene.update()
            current_cutscene.draw(screen, SCREEN_SIZE)
            
            pygame.display.flip()
            continue

        if game_state == 'night_cutscene':
            # Draw the game world in background (frozen)
            sky_color = get_sky_color(day_timer, DAY_LENGTH, NIGHT_LENGTH)
            screen.fill(sky_color)
            
            # Draw ground texture
            ground.draw(screen, camera.offset)
            
            # Draw obstacles
            for ob in obstacles:
                screen.blit(ob.base_image, camera.apply(ob.collision_rect).topleft)
            
            # Draw enemies
            for en in sorted(enemies, key=lambda e: e.pos.y):
                screen.blit(en.image, camera.apply(en.rect).topleft)
            
            # Draw player (in transition)
            screen.blit(player.image, camera.apply(player.rect).topleft)
            
            # Draw top parts
            for ob in obstacles:
                if ob.top_image:
                    screen.blit(ob.top_image, camera.apply(ob.top_rect).topleft)
            
            # Night darkness
            dark = pygame.Surface(SCREEN_SIZE, pygame.SRCALPHA)
            dark.fill((0, 0, 0, DARK_ALPHA))
            screen.blit(dark, (0, 0))
            
            # Sky gradient
            gradient_height = 60
            gradient_surf = pygame.Surface((SCREEN_SIZE[0], gradient_height), pygame.SRCALPHA)
            for y in range(gradient_height):
                alpha = int(255 * (1 - y / gradient_height) * 0.7)
                color = sky_color + (alpha,)
                pygame.draw.line(gradient_surf, color, (0, y), (SCREEN_SIZE[0], y))
            screen.blit(gradient_surf, (0, 0))
            
            # Update and draw cutscene
            current_cutscene.update()
            current_cutscene.draw(screen, SCREEN_SIZE)
            
            pygame.display.flip()
            continue


        if game_state == 'playing':
            # update day/night timer
            day_timer += dt
            cycle_len = DAY_LENGTH + NIGHT_LENGTH
            cycle_t = day_timer % cycle_len
            was_night = is_night
            if cycle_t < DAY_LENGTH:
                is_night = False
            else:
                is_night = True

            # transition into night: play transition frames then switch to night anims
            if is_night and not was_night:
                # Show night cutscene only on first transition
                if not night_cutscene_shown:
                    current_cutscene = create_night_cutscene(font)
                    game_state = 'night_cutscene'
                    night_cutscene_shown = True
                    
                    # Prepare transition animations
                    player.anim = {state: {facing: frames[:] for facing, frames in dirs.items()} for state, dirs in player_anims.items()}
                    for state in trans_anims:
                        player.anim[state] = trans_anims[state]
                    
                    # Start transition animation
                    player.play_transition_animation()
                    
                    # Halt enemies during cutscene
                    for en in enemies:
                        en.mode = 'halt'
                    
                    # Start night music
                    audio.play_music(MUSIC_NIGHT, MUSIC_VOLUME['night'], loops=-1)
                    
                    continue  # Skip the rest of this frame
                else:
                    # Subsequent night transitions (no cutscene)
                    player.anim = {state: {facing: frames[:] for facing, frames in dirs.items()} for state, dirs in player_anims.items()}
                    for state in trans_anims:
                        player.anim[state] = trans_anims[state]
                    
                    player.play_transition_animation()
                    
                    night_phase = 'idle_halt'
                    night_phase_timer = TRANSITION_MS / 1000.0
                    for en in enemies:
                        en.mode = 'halt'
                    
                    # Start night music
                    audio.play_music(MUSIC_NIGHT, MUSIC_VOLUME['night'], loops=-1)

            # handle night phases
            if is_night:
                if night_phase == 'idle_halt':
                    night_phase_timer -= dt
                    if night_phase_timer <= 0:
                        # transition complete: switch player anims to actual night sheet and let enemies flee
                        player.anim = player_night_anims
                        # ensure player's frame/state resets so run works
                        player.stop_night_animation()
                        player.frame_idx = 0
                        player.last_frame_time = pygame.time.get_ticks()
                        player.pause_until = 0
                        night_phase = 'flee'
                        for en in enemies:
                            en.mode = 'flee'
                            en.last_recalc = -9999.0
                elif night_phase == 'flee':
                    # enemies flee; nothing else forced on player
                    pass
            else:
                # day resumed: ensure player uses day animations and enemies chase
                if night_phase != 'none':
                    # Create a fresh copy of day animations (without transition state)
                    player.anim = {state: {facing: frames[:] for facing, frames in dirs.items()} for state, dirs in player_anims.items()}
                    player.stop_night_animation()
                    player.frame_idx = 0
                    player.last_frame_time = pygame.time.get_ticks()
                    night_phase = 'none'
                    for en in enemies:
                        en.mode = 'chase'
                        en.last_recalc = -9999.0
                    
                    # Resume day music
                    audio.play_music(MUSIC_DAY, MUSIC_VOLUME['day'], loops=-1)

            # Update player
            player.update(dt, keys, allow_control=True)

            # Player vs obstacles collision (rect then mask)
            for ob in obstacles:
                if player.rect.colliderect(ob.collision_rect):
                    offset = (ob.collision_rect.left - player.rect.left, ob.collision_rect.top - player.rect.top)
                    if player.mask.overlap(ob.collision_mask, offset):
                        if player.collide_with_obstacle(ob) and SHAKE_ON_OBSTACLE:
                            camera.shake()
                        break

            # Update enemies
            now_sec = pygame.time.get_ticks() / 1000.0
            for en in list(enemies):
                # handle hit/despawn and award heart on actual removal
                if en.hit:
                    if pygame.time.get_ticks() - en.hit_time >= ENEMY_DESPAWN_MS:
                        player.hearts = min(99, player.hearts + 1)
                        player.gain_heart()  # Play heal sound
                        enemies.remove(en)
                        # Play rip sound when enemy despawns
                        audio.play_sound('rip')
                    continue
                if en.mode == 'halt':
                    continue
                en.update(dt, player, obstacles, enemies, now_sec)

            # Enemy-player collision
            for en in list(enemies):
                # Skip collision check if enemy is already hit (being eaten)
                if en.hit:
                    continue
                    
                if en.rect.colliderect(player.rect):
                    offset = (en.rect.left - player.rect.left, en.rect.top - player.rect.top)
                    if player.mask.overlap(en.mask, offset):
                        if is_night and night_phase == 'flee':
                            # catch fleeing enemy: mark it hit (will despawn after ENEMY_DESPAWN_MS)
                            player.pause_until = pygame.time.get_ticks() + PLAYER_PAUSE_ON_CATCH_MS
                            en.hit = True
                            en.hit_time = pygame.time.get_ticks()
                        else:
                            # daytime hit: lose a heart and get knocked back
                            player.hearts = max(0, player.hearts - 1)
                            if player.hit_by_enemy(en) and SHAKE_ON_HIT:
                                camera.shake()
                            en.vel *= -0.3
                        break

            camera.update(player.rect, player.vel)

            sky_color = get_sky_color(day_timer, DAY_LENGTH, NIGHT_LENGTH)

            screen.fill(sky_color)  # Fill with sky color as background
            
            ground.draw(screen, camera.offset)

            for ob in obstacles:
                screen.blit(ob.base_image, camera.apply(ob.collision_rect).topleft)

            for en in sorted(enemies, key=lambda e: e.pos.y):
                img = en.image.copy()
                if en.hit:
                    overlay = pygame.Surface(img.get_size(), pygame.SRCALPHA)
                    overlay.fill((255, 0, 0, 140))
                    img.blit(overlay, (0, 0), special_flags=pygame.BLEND_RGBA_ADD)
                screen.blit(img, camera.apply(en.rect).topleft)

            player_draw_img = player.image.copy()
            if pygame.time.get_ticks() < player.flash_until:
                overlay = pygame.Surface(player_draw_img.get_size(), pygame.SRCALPHA)
                overlay.fill((255, 0, 0, 100))
                player_draw_img.blit(overlay, (0, 0), special_flags=pygame.BLEND_RGBA_ADD)
            screen.blit(player_draw_img, camera.apply(player.rect).topleft)

            for ob in obstacles:
                if ob.top_image:
                    screen.blit(ob.top_image, camera.apply(ob.top_rect).topleft)

            if is_night:
                dark = pygame.Surface(SCREEN_SIZE, pygame.SRCALPHA)
                dark.fill((0, 0, 0, DARK_ALPHA))
                screen.blit(dark, (0, 0))

            gradient_height = 60
            gradient_surf = pygame.Surface((SCREEN_SIZE[0], gradient_height), pygame.SRCALPHA)
            for y in range(gradient_height):
                alpha = int(255 * (1 - y / gradient_height) * 0.7)  # Fade out towards bottom
                color = sky_color + (alpha,)
                pygame.draw.line(gradient_surf, color, (0, y), (SCREEN_SIZE[0], y))
            screen.blit(gradient_surf, (0, 0))

            padding = 8
            for i in range(player.hearts):
                x = padding + i * (heart_img.get_width() + 4)
                y = padding
                screen.blit(heart_img, (x, y))

            bar_w = 160
            bar_h = 14
            bar_x = SCREEN_SIZE[0] - bar_w - 12
            bar_y = 12
            pygame.draw.rect(screen, (40, 40, 40), (bar_x, bar_y, bar_w, bar_h))
            perc = player.stamina / STAMINA_MAX
            inner_w = int(bar_w * perc)
            pygame.draw.rect(screen, (80, 200, 120), (bar_x + 2, bar_y + 2, max(0, inner_w - 4), bar_h - 4))
            stext = font.render("Stamina", True, (255, 255, 255))
            screen.blit(stext, (bar_x - 86, bar_y - 2))
            
            shader.apply_effects(screen)

            if player.hearts <= 0:
                game_state = 'died'
                # Stop movement sounds and play death music
                audio.stop_movement_sounds()
                audio.play_music(MUSIC_RESPAWN, MUSIC_VOLUME['respawn'], loops=0)
            elif len(enemies) == 0:
                game_state = 'won'
                # Stop movement sounds and play victory music
                audio.stop_movement_sounds()
                audio.play_music(MUSIC_YOUWON, MUSIC_VOLUME['youwon'], loops=0)

            pygame.display.flip()
            continue

        if game_state == 'died':
            screen.fill((0, 0, 0))
            screen.blit(died_img, (0, 0))
            screen.blit(back_btn_img, back_btn.topleft)
            pygame.display.flip()
            continue

        if game_state == 'won':
            screen.fill((0, 0, 0))
            screen.blit(win_img, (0, 0))
            screen.blit(back_btn_img, back_btn.topleft)
            pygame.display.flip()
            continue

    pygame.quit()


if __name__ == '__main__':
    main()
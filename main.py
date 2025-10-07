"""
Top-down Pygame demo (full rewrite):
- Movement with acceleration + friction for realistic running
- Master spritesheet loader (rows = different animation strips)
- Flexible SHEET_LAYOUT to pick specific rows (state+facing) and frame counts
- Animated frames for idle/run per direction, with independent frame timings
- Pixel-perfect collisions using masks
- Random obstacles (trees/rocks) with knockback + freeze on collision

ASSET USAGE (edit these):
- MASTER_SHEET: a single PNG that contains multiple horizontal strips (rows).
  Each row is an animation strip (n frames in that row). Use SHEET_LAYOUT below
  to pick which row corresponds to which (state,facing).
- You can still provide separate obstacle images under assets/obstacles/

Drop this file and run. Edit the ASSET PATHS and SHEET_LAYOUT at the top.

Author: ChatGPT (patfor ob in obstacles:ched with your requests). :>
"""

import os
import sys
import random
import math
import pygame
from pygame.math import Vector2

# --------------------- USER CONFIG (edit this) ---------------------
# Where your master sheet lives (single PNG with many horizontal strips)
ASSET_DIR = os.path.join(os.path.dirname(__file__), 'assets')
MASTER_SHEET = os.path.join(ASSET_DIR, 'player', 'Blacksmith.png')

# If your sheet has fixed frame size, set these. If unsure, inspect your sheet.
FRAME_WIDTH = 64    # pixel width of each frame in the sheet
FRAME_HEIGHT = 64   # pixel height of each frame in the sheet
SHEET_SCALE = 1.0   # scale factor applied to frames after slicing

# Describe exactly which rows to use from the master sheet.
# Each entry picks a row index (0-based), the state name, facing name, and number of frames in that row.
# Example: row 0 is idle down (4 frames), row 1 is run down (6 frames), etc.
# If `frames` is None the loader will read as many frames as fit in the row.
# You can include only the rows you care about.
SHEET_LAYOUT = [
    # row_index, state, facing, frames (None => auto)
    {'row': 10, 'state': 'idle', 'facing': 'down',  'frames': 1},
    {'row': 10, 'state': 'run',  'facing': 'down',  'frames': 9},
    {'row': 9, 'state': 'idle', 'facing': 'left',  'frames': 1},
    {'row': 9, 'state': 'run',  'facing': 'left',  'frames': 9},
    {'row': 11, 'state': 'idle', 'facing': 'right', 'frames': 1},
    {'row': 11, 'state': 'run',  'facing': 'right', 'frames': 9},
    {'row': 8, 'state': 'idle', 'facing': 'up',    'frames': 1},
    {'row': 8, 'state': 'run',  'facing': 'up',    'frames': 8},
]
# If your sheet rows are in a different order, edit SHEET_LAYOUT accordingly.

# Per-state frame durations (milliseconds per frame)
FRAME_DURATION = {
    'idle': 220,
    'run' : 80,
}




# Game tuning
SCREEN_SIZE = (800, 600)
WORLD_SIZE = (2000, 2000)
FPS = 60

MAX_SPEED = 300.0
ACCELERATION = 1800.0
FRICTION = 2000.0
KNOCKBACK_SPEED = 240.0
FREEZE_MS = 500
OBSTACLE_COUNT = 60
OBSTACLE_MIN_DIST = 140

# -------------------- END USER CONFIG --------------------



# Slice a horizontal row from a master sheet into frames
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
        else:
            break
    return frames

# Load entire master sheet and build the animations dictionary using SHEET_LAYOUT
def build_animations_from_master(path, frame_w, frame_h, layout, scale=1.0):
    if not os.path.isfile(path):
        print(f"Master sheet not found at {path}. Using single fallback frame for all animations.")
        # Create fallback single frame
        fallback = pygame.Surface((frame_w, frame_h), pygame.SRCALPHA)
        fallback.fill((200,100,100))
        return {'idle': {'down':[fallback], 'up':[fallback], 'left':[fallback], 'right':[fallback]},
                'run' : {'down':[fallback], 'up':[fallback], 'left':[fallback], 'right':[fallback]}}

    sheet = pygame.image.load(path).convert_alpha()
    anims = {}
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
    # Ensure required keys exist (so code doesn't KeyError)
    for st in ['idle','run']:
        if st not in anims:
            anims[st] = {}
        for dirn in ['up','down','left','right']:
            if dirn not in anims[st] or len(anims[st][dirn]) == 0:
                # fallback single-frame surface
                s = pygame.Surface((frame_w, frame_h), pygame.SRCALPHA)
                s.fill((150,150,150))
                anims[st][dirn] = [s]
    return anims

class Camera:
    def __init__(self, screen_size, world_size):
        self.screen_w, self.screen_h = screen_size
        self.world_w, self.world_h = world_size
        self.offset = Vector2(0,0)
    def update(self, target_rect):
        x = target_rect.centerx - self.screen_w//2
        y = target_rect.centery - self.screen_h//2
        x = max(0, min(x, self.world_w - self.screen_w))
        y = max(0, min(y, self.world_h - self.screen_h))
        self.offset.update(x, y)
    def apply(self, rect):
        return rect.move(-int(self.offset.x), -int(self.offset.y))

class Obstacle(pygame.sprite.Sprite):
    def __init__(self, base_image, top_image, pos):
        """
        base_image: surface used for collision and bottom drawing (trunk)
        top_image: surface drawn *after* player (canopy). May be None.
        pos: center position tuple
        """
        super().__init__()
        self.base_image = base_image
        self.top_image = top_image  # may be None
        self.image = base_image     # used if you want a default
        self.rect = self.base_image.get_rect(center=pos)

        # collision mask & rect use base_image only (trunk)
        self.collision_mask = pygame.mask.from_surface(self.base_image)
        self.collision_rect = self.base_image.get_rect(center=pos)

        # for drawing the top part we want full bounds (use top_image rect if exists)
        if self.top_image:
            self.top_rect = self.top_image.get_rect(center=pos)
        else:
            self.top_rect = None


class Player(pygame.sprite.Sprite):
    def __init__(self, animations, pos, frame_durations=None):
        super().__init__()
        self.anim = animations
        self.state = 'idle'
        self.facing = 'down'
        self.frame_idx = 0
        self.frame_durations = frame_durations or FRAME_DURATION
        self.last_frame_time = pygame.time.get_ticks()

        self.current_frames = self.anim[self.state][self.facing]
        self.image = self.current_frames[self.frame_idx]
        self.rect = self.image.get_rect(center=pos)
        self.mask = pygame.mask.from_surface(self.image)

        self.pos = Vector2(pos)
        self.vel = Vector2(0,0)
        self.acc = Vector2(0,0)

        self.freeze_until = 0

    def update(self, dt, keys):
        now = pygame.time.get_ticks()
        if now < self.freeze_until:
            self.vel *= 0.9
            self.pos += self.vel * dt
            self.rect.center = (int(self.pos.x), int(self.pos.y))
            return

        move = Vector2(0,0)
        if keys[pygame.K_w] or keys[pygame.K_UP]: move.y = -1
        if keys[pygame.K_s] or keys[pygame.K_DOWN]: move.y = 1
        if keys[pygame.K_a] or keys[pygame.K_LEFT]: move.x = -1
        if keys[pygame.K_d] or keys[pygame.K_RIGHT]: move.x = 1

        if move.length_squared() > 0:
            move = move.normalize()
            desired = move * MAX_SPEED
            change = desired - self.vel
            max_change = ACCELERATION * dt
            if change.length() > max_change:
                change = change.normalize() * max_change
            self.vel += change
        else:
            if self.vel.length_squared() > 0:
                decel = FRICTION * dt
                if self.vel.length() <= decel:
                    self.vel = Vector2(0,0)
                else:
                    self.vel -= self.vel.normalize() * decel

        if self.vel.length() > MAX_SPEED:
            self.vel.scale_to_length(MAX_SPEED)

        # update position
        self.pos += self.vel * dt
        self.pos.x = max(0, min(self.pos.x, WORLD_SIZE[0]))
        self.pos.y = max(0, min(self.pos.y, WORLD_SIZE[1]))
        self.rect.center = (int(self.pos.x), int(self.pos.y))

        # Determine state & facing
        prev_state = self.state
        prev_facing = self.facing
        if self.vel.length_squared() > 10:
            self.state = 'run'
            vx, vy = self.vel.x, self.vel.y
            if abs(vx) >= abs(vy):
                self.facing = 'right' if vx > 0 else 'left'
            else:
                self.facing = 'down' if vy > 0 else 'up'
        else:
            self.state = 'idle'

        # Reset frame if state/facing changed
        if self.state != prev_state or self.facing != prev_facing:
            self.frame_idx = 0
            self.last_frame_time = now

        # Update animation frames
        self.current_frames = self.anim[self.state][self.facing]
        duration = self.frame_durations.get(self.state, 100)
        if now - self.last_frame_time >= duration:
            self.frame_idx = (self.frame_idx + 1) % len(self.current_frames)
            self.last_frame_time = now
            self.image = self.current_frames[self.frame_idx]
            self.mask = pygame.mask.from_surface(self.image)

    def collide_with(self, obstacle):
        dir_vec = (self.pos - Vector2(obstacle.rect.center))
        if dir_vec.length_squared() == 0:
            dir_vec = Vector2(random.uniform(-1,1), random.uniform(-1,1))
        dir_vec = dir_vec.normalize()
        self.vel = dir_vec * KNOCKBACK_SPEED
        self.freeze_until = pygame.time.get_ticks() + FREEZE_MS

def place_obstacles(count, avoid_pos, min_dist, world_size, asset_pairs):
    """
    asset_pairs: list of (base_surface, top_surface_or_None) tuples
    returns: pygame.sprite.Group() of Obstacle instances
    """
    obstacles = pygame.sprite.Group()
    attempts = 0
    placed = 0
    while placed < count and attempts < count * 30:
        attempts += 1
        x = random.randint(64, world_size[0] - 64)
        y = random.randint(64, world_size[1] - 64)
        pos = Vector2(x,y)
        if pos.distance_to(Vector2(avoid_pos)) < min_dist:
            continue
        base_surf, top_surf = random.choice(asset_pairs)   # unpack pair
        ob = Obstacle(base_surf, top_surf, pos)            # matches your Obstacle signature
        # simple overlap check against placed obstacles
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


# Main
def main():
    pygame.init()
    screen = pygame.display.set_mode(SCREEN_SIZE)
    pygame.display.set_caption('Top-down: master-sheet animations + mask collisions')
    clock = pygame.time.Clock()

    # Build animations
    animations = build_animations_from_master(MASTER_SHEET, FRAME_WIDTH, FRAME_HEIGHT, SHEET_LAYOUT, scale=SHEET_SCALE)

    player_start = (WORLD_SIZE[0]//2, WORLD_SIZE[1]//2)
    player = Player(animations, player_start, frame_durations=FRAME_DURATION)

    camera = Camera(SCREEN_SIZE, WORLD_SIZE)

    running = True

    # Utility: safe image loader with fallback
    def load_image(path, fallback_size=(48,48)):
        if path and os.path.isfile(path):
            try:
                return pygame.image.load(path).convert_alpha()
            except Exception as e:
                print(f"Failed loading {path}: {e}")
        surf = pygame.Surface(fallback_size, pygame.SRCALPHA)
        surf.fill((180, 180, 180, 255))
        pygame.draw.rect(surf, (0,0,0), surf.get_rect(), 2)
        return surf

    # load once
    tree_base = load_image(os.path.join(ASSET_DIR, 'obstacles', 'treebase.png'))
    tree_top  = load_image(os.path.join(ASSET_DIR, 'obstacles', 'treetop.png'))
    rock_base = load_image(os.path.join(ASSET_DIR, 'obstacles', 'rock.png'))
    rock_top  = None   # rock has no canopy

    # list of (base_surface, top_surface) pairs
    OBSTACLE_ASSET_PAIRS = [
        (tree_base, tree_top),
        (rock_base, rock_top),
    ]

    obstacles = place_obstacles(OBSTACLE_COUNT, player_start, OBSTACLE_MIN_DIST, WORLD_SIZE, OBSTACLE_ASSET_PAIRS)
    while running:
        dt = clock.tick(FPS) / 1000.0
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                running = False

        keys = pygame.key.get_pressed()
        player.update(dt, keys)

        # Collision: rect then mask
        for ob in obstacles:
            if player.rect.colliderect(ob.collision_rect):
                offset = (ob.collision_rect.left - player.rect.left,
                        ob.collision_rect.top  - player.rect.top)
                if player.mask.overlap(ob.collision_mask, offset):
                    player.collide_with(ob)
                    break

        camera.update(player.rect)

        # Draw
        screen.fill((102,170,255))
        ground_rect = pygame.Rect(-int(camera.offset.x), -int(camera.offset.y), WORLD_SIZE[0], WORLD_SIZE[1])
        pygame.draw.rect(screen, (30,120,30), ground_rect)

        # collision check (player is your Player instance)
        for ob in obstacles:
            if player.rect.colliderect(ob.collision_rect):
                offset = (ob.collision_rect.left - player.rect.left, ob.collision_rect.top - player.rect.top)
                if player.mask.overlap(ob.collision_mask, offset):
                    player.collide_with(ob)
                    break

        # draw base parts before player
        for ob in obstacles:
            screen.blit(ob.base_image, camera.apply(ob.collision_rect).topleft)

        # draw player
        screen.blit(player.image, camera.apply(player.rect).topleft)

        # draw top parts (canopy) after player
        for ob in obstacles:
            if ob.top_image:
                screen.blit(ob.top_image, camera.apply(ob.top_rect).topleft)


        pygame.display.flip()

    pygame.quit()

if __name__ == '__main__':
    main()

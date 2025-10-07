# topdown_a_star_4dir_daynight_menu.py
"""
Top-down Pygame demo (A* nav + enemies randomized animated sprites + 4-direction player)
Features added/changed from previous version:
 - All animations are 4-directional (up/down/left/right)
 - Run animation speed syncs to player velocity so sprint looks right (tweakable)
 - Enemies randomly pick one spritesheet from assets/enemies/ (each sheet must include 4-dir idle/run)
 - Enemies use A* on a nav grid and maintain separation (avoid blob)
 - DAY / NIGHT cycle:
     * Day: normal gameplay (enemies chase the player)
     * Night start: scene darkens; player plays a 'night' animation and is halted for NIGHT_IDLE_MS
       enemies also halt during that short window
     * After that, enemies switch to FLEE mode (they run away using A*), and player may chase them
     * If player catches (collides with) an enemy while in FLEE, player gains a heart, enemy flashes red then despawns,
       and player is briefly paused
     * When all enemies are gone -> WIN screen with an image and a button to return to menu
 - Simple main menu (background image + Start button). From menu you start the game.

USAGE:
 - Put your player master sheet at MASTER_SHEET and configure PLAYER_SHEET_LAYOUT rows for idle/run/night states.
 - Put 1..N enemy sheets in assets/enemies/ following ENEMY_SHEET_LAYOUT (idle/run rows for 4 directions).
 - Place obstacle images under assets/obstacles/ as before.
 - Provide optional menu background and win image under assets/ui/menu_bg.png and assets/ui/win.png

Author: ChatGPT — refined per your requests :>
"""

import os
import sys
import random
import math
import heapq
import pygame
from pygame.math import Vector2

# --------------------- USER CONFIG (edit this) ---------------------
ASSET_DIR = os.path.join(os.path.dirname(__file__), 'assets')
MASTER_SHEET = os.path.join(ASSET_DIR, 'player', 'Blacksmith.png')
ENEMY_SPRITES_DIR = os.path.join(ASSET_DIR, 'enemies')
HEART_IMG = os.path.join(ASSET_DIR, 'ui', 'heart.png')
MENU_BG = os.path.join(ASSET_DIR, 'ui', 'menu_bg.png')
WIN_IMG = os.path.join(ASSET_DIR, 'ui', 'win.png')

FRAME_WIDTH = 64
FRAME_HEIGHT = 64
SHEET_SCALE = 1.0

# PLAYER: 4-direction layout. Edit row indices to match your sheet.
PLAYER_SHEET_LAYOUT = [
    {'row': 0, 'state': 'idle', 'facing': 'down',  'frames': 1},
    {'row': 1, 'state': 'idle', 'facing': 'left',  'frames': 1},
    {'row': 2, 'state': 'idle', 'facing': 'right', 'frames': 1},
    {'row': 3, 'state': 'idle', 'facing': 'up',    'frames': 1},
    {'row': 4, 'state': 'run',  'facing': 'down',  'frames': 6},
    {'row': 5, 'state': 'run',  'facing': 'left',  'frames': 6},
    {'row': 6, 'state': 'run',  'facing': 'right', 'frames': 6},
    {'row': 7, 'state': 'run',  'facing': 'up',    'frames': 6},
    # optional night animation rows (player halts and plays this)
    {'row': 8, 'state': 'night', 'facing': 'down',  'frames': 4},
    {'row': 9, 'state': 'night', 'facing': 'left',  'frames': 4},
    {'row':10, 'state': 'night', 'facing': 'right', 'frames': 4},
    {'row':11, 'state': 'night', 'facing': 'up',    'frames': 4},
]

# ENEMY sheet layout for 4-directions (idle/run). Put enemy pngs in ENEMY_SPRITES_DIR
ENEMY_SHEET_LAYOUT = [
    {'row': 0, 'state': 'idle', 'facing': 'down',  'frames': 1},
    {'row': 1, 'state': 'idle', 'facing': 'left',  'frames': 1},
    {'row': 2, 'state': 'idle', 'facing': 'right', 'frames': 1},
    {'row': 3, 'state': 'idle', 'facing': 'up',    'frames': 1},
    {'row': 4, 'state': 'run',  'facing': 'down',  'frames': 6},
    {'row': 5, 'state': 'run',  'facing': 'left',  'frames': 6},
    {'row': 6, 'state': 'run',  'facing': 'right', 'frames': 6},
    {'row': 7, 'state': 'run',  'facing': 'up',    'frames': 6},
]

FRAME_DURATION = {'idle': 220, 'run': 100, 'night': 140}

# Game tuning
SCREEN_SIZE = (800, 600)
WORLD_SIZE = (2000, 2000)
FPS = 60

MAX_SPEED = 300.0
ACCELERATION = 1800.0
FRICTION = 2000.0
KNOCKBACK_SPEED = 240.0

# obstacles
OBSTACLE_COUNT = 60
OBSTACLE_MIN_DIST = 140

# enemies
ENEMY_COUNT = 10
ENEMY_SPAWN_MIN_DIST = 300
ENEMY_MAX_SPEED = 140.0
ENEMY_ACCELERATION = 900.0

# A* nav grid tuning
NAV_CELL_SIZE = 48
NAV_EXPAND_CELLS = 1
PATH_RECALC_INTERVAL = 0.85
PLAYER_MOVE_REPATH_DIST = 64

# enemy separation
SEPARATION_RADIUS = 36.0
SEPARATION_FORCE = 420.0

# hearts & hit
PLAYER_MAX_HEARTS = 5
HIT_FLASH_MS = 200

# sprint system
SPRINT_MULTIPLIER = 1.60
STAMINA_MAX = 5.0
STAMINA_DRAIN_PER_SEC = 1.2
STAMINA_RECOVER_PER_SEC = 0.8
STAMINA_MIN_TO_SPRINT = 0.2

# DAY/NIGHT
DAY_LENGTH = 20.0            # seconds of daytime
NIGHT_LENGTH = 12.0         # seconds of night cycle (includes halt+flee)
NIGHT_IDLE_MS = 1500        # how long player/enemies halt and player plays night animation (ms)
DARK_ALPHA = 190            # how dark the screen becomes at night (0..255)

# catch behavior
ENEMY_DESPAWN_MS = 700      # after caught, how long until enemy is removed
PLAYER_PAUSE_ON_CATCH_MS = 800

PLACEMENT_ATTEMPTS_MULT = 30
# -------------------- END USER CONFIG --------------------

# -------------------- helpers --------------------

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


def build_animations_from_master(path, frame_w, frame_h, layout, scale=1.0):
    # If missing, returns fallback minimal animation dict for states ['idle','run','night'] and facings [up/down/left/right]
    if not os.path.isfile(path):
        fallback = pygame.Surface((frame_w, frame_h), pygame.SRCALPHA)
        fallback.fill((200,100,100,255))
        anims = {}
        for st in ['idle','run','night']:
            anims[st] = {}
            for f in ['down','left','right','up']:
                anims[st][f] = [fallback]
        return anims

    sheet = pygame.image.load(path).convert_alpha()
    anims = {}
    for entry in layout:
        row = entry['row']; state = entry['state']; facing = entry['facing']
        frames_count = entry.get('frames', None)
        frames = slice_row(sheet, row, frame_w, frame_h, frames_count)
        if scale != 1.0:
            frames = [pygame.transform.scale(f, (int(f.get_width()*scale), int(f.get_height()*scale))) for f in frames]
        if state not in anims:
            anims[state] = {}
        anims[state][facing] = frames
    # ensure all keys exist
    for st in ['idle','run','night']:
        if st not in anims: anims[st] = {}
        for dirn in ['down','left','right','up']:
            if dirn not in anims[st] or len(anims[st][dirn]) == 0:
                s = pygame.Surface((frame_w, frame_h), pygame.SRCALPHA); s.fill((150,150,150))
                anims[st][dirn] = [s]
    return anims


def facing_from_vector(vec):
    # 4-direction mapping using velocity vector
    if vec.length_squared() == 0:
        return 'down'
    vx, vy = vec.x, vec.y
    if abs(vx) > abs(vy):
        return 'right' if vx > 0 else 'left'
    else:
        return 'down' if vy > 0 else 'up'

# ------------------------------ camera/obstacle/player classes ------------------------------
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
        super().__init__()
        self.base_image = base_image
        self.top_image = top_image
        self.rect = self.base_image.get_rect(center=pos)
        self.collision_mask = pygame.mask.from_surface(self.base_image)
        self.collision_rect = self.base_image.get_rect(center=pos)
        self.top_rect = self.top_image.get_rect(center=pos) if self.top_image else None

class Player(pygame.sprite.Sprite):
    def __init__(self, animations, pos, frame_durations=None):
        super().__init__()
        self.anim = animations
        self.state = 'idle'; self.facing = 'down'; self.frame_idx = 0
        self.frame_durations = frame_durations or FRAME_DURATION
        self.last_frame_time = pygame.time.get_ticks()
        self.current_frames = self.anim[self.state][self.facing]
        self.image = self.current_frames[self.frame_idx]
        self.rect = self.image.get_rect(center=pos)
        self.mask = pygame.mask.from_surface(self.image)
        self.pos = Vector2(pos); self.vel = Vector2(0,0); self.acc = Vector2(0,0)
        self.stamina = STAMINA_MAX; self.hearts = PLAYER_MAX_HEARTS
        self.flash_until = 0; self.freeze_until = 0
        self.pause_until = 0

    def update(self, dt, keys, allow_control=True):
        now_ms = pygame.time.get_ticks()
        if now_ms < self.pause_until:
            # paused (e.g., after catch); still update animation but no movement
            self.vel *= 0.9
            self.pos += self.vel * dt
            self.rect.center = (int(self.pos.x), int(self.pos.y))
            # update anim without changing frames much
            self._update_anim_speed_synced()
            return

        if now_ms < self.freeze_until:
            # frozen from obstacle collision
            self.vel *= 0.9
            self.pos += self.vel * dt
            self.rect.center = (int(self.pos.x), int(self.pos.y))
            self._update_anim_speed_synced()
            return

        sprinting = (keys[pygame.K_LSHIFT] or keys[pygame.K_RSHIFT]) and self.stamina > STAMINA_MIN_TO_SPRINT and allow_control
        move = Vector2(0,0)
        if allow_control:
            if keys[pygame.K_w] or keys[pygame.K_UP]: move.y = -1
            if keys[pygame.K_s] or keys[pygame.K_DOWN]: move.y = 1
            if keys[pygame.K_a] or keys[pygame.K_LEFT]: move.x = -1
            if keys[pygame.K_d] or keys[pygame.K_RIGHT]: move.x = 1

        speed_cap = MAX_SPEED * (SPRINT_MULTIPLIER if sprinting else 1.0)

        if move.length_squared() > 0:
            move = move.normalize()
            desired = move * speed_cap
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

        if self.vel.length() > speed_cap:
            self.vel.scale_to_length(speed_cap)

        # update position
        self.pos += self.vel * dt
        self.pos.x = max(0, min(self.pos.x, WORLD_SIZE[0]))
        self.pos.y = max(0, min(self.pos.y, WORLD_SIZE[1]))
        self.rect.center = (int(self.pos.x), int(self.pos.y))

        # Determine state & facing
        prev_state, prev_facing = self.state, self.facing
        if self.vel.length_squared() > 10:
            self.state = 'run'
            self.facing = facing_from_vector(self.vel)
        else:
            self.state = 'idle'
        if self.state != prev_state or self.facing != prev_facing:
            self.frame_idx = 0; self.last_frame_time = pygame.time.get_ticks()

        # animation speed synced to velocity
        self._update_anim_speed_synced()

        # stamina update
        if sprinting and move.length_squared() > 0:
            self.stamina -= STAMINA_DRAIN_PER_SEC * dt
            self.stamina = max(0.0, self.stamina)
        else:
            self.stamina += STAMINA_RECOVER_PER_SEC * dt
            self.stamina = min(STAMINA_MAX, self.stamina)

    def _update_anim_speed_synced(self):
        now = pygame.time.get_ticks()
        self.current_frames = self.anim[self.state].get(self.facing, self.anim[self.state]['down'])
        base_duration = self.frame_durations.get(self.state, 100)
        speed = self.vel.length()
        max_possible = MAX_SPEED * SPRINT_MULTIPLIER
        speed_ratio = min(1.0, speed / max_possible)
        scale = 1.4 - 0.8 * speed_ratio
        duration = max(25, int(base_duration * scale))
        if now - self.last_frame_time >= duration:
            self.frame_idx = (self.frame_idx + 1) % len(self.current_frames)
            self.last_frame_time = now
            self.image = self.current_frames[self.frame_idx]
            self.mask = pygame.mask.from_surface(self.image)

    def collide_with_obstacle(self, obstacle):
        dir_vec = (self.pos - Vector2(obstacle.collision_rect.center))
        if dir_vec.length_squared() == 0:
            dir_vec = Vector2(random.uniform(-1,1), random.uniform(-1,1))
        dir_vec = dir_vec.normalize()
        self.vel = dir_vec * KNOCKBACK_SPEED
        self.freeze_until = pygame.time.get_ticks() + 500

    def hit_by_enemy(self, enemy):
        dir_vec = (self.pos - Vector2(enemy.rect.center))
        if dir_vec.length_squared() == 0:
            dir_vec = Vector2(random.uniform(-1,1), random.uniform(-1,1))
        dir_vec = dir_vec.normalize()
        self.vel = dir_vec * KNOCKBACK_SPEED
        # previously losing hearts; changed per night mechanic: enemies caught grant hearts
        # keep flash to indicate hit
        self.flash_until = pygame.time.get_ticks() + HIT_FLASH_MS

# ------------------------------ NAV / A* helpers ------------------------------
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
    cx = int(pos.x // cell_size); cy = int(pos.y // cell_size)
    return cx, cy

def cell_to_world_center(cx, cy, cell_size):
    x = cx * cell_size + cell_size // 2
    y = cy * cell_size + cell_size // 2
    return Vector2(x, y)

def neighbors_for(cx, cy, grid):
    rows = len(grid); cols = len(grid[0])
    nbrs = []
    for dy in (-1, 0, 1):
        for dx in (-1, 0, 1):
            if dx == 0 and dy == 0: continue
            nx = cx + dx; ny = cy + dy
            if 0 <= nx < cols and 0 <= ny < rows and grid[ny][nx] == 0:
                cost = math.hypot(dx, dy)
                nbrs.append((nx, ny, cost))
    return nbrs

def heuristic(a, b):
    (ax, ay) = a; (bx, by) = b
    return math.hypot(bx - ax, by - ay)

def a_star(grid, start, goal, max_nodes=25000):
    if start == goal: return [start]
    rows = len(grid); cols = len(grid[0])
    sx, sy = start; gx, gy = goal
    if not (0 <= sx < cols and 0 <= sy < rows): return None
    if not (0 <= gx < cols and 0 <= gy < rows): return None
    if grid[sy][sx] == 1 or grid[gy][gx] == 1: return None
    open_heap = []
    heapq.heappush(open_heap, (0 + heuristic(start, goal), 0, start))
    came_from = {}
    gscore = {start: 0}
    visited = 0
    while open_heap:
        f, g, current = heapq.heappop(open_heap)
        visited += 1
        if visited > max_nodes: return None
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

# ------------------------------ Enemy class (4-dir, A* path, separation, modes) ------------------------------
class Enemy(pygame.sprite.Sprite):
    def __init__(self, pos, nav_grid, cell_size, anims, frame_durations, image_radius=18):
        super().__init__()
        self.anims = anims
        self.frame_durations = frame_durations or FRAME_DURATION
        self.state = 'idle'; self.facing = 'down'; self.frame_idx = 0
        self.last_frame_time = pygame.time.get_ticks()
        self.current_frames = self.anims[self.state][self.facing]
        self.image = self.current_frames[self.frame_idx]
        self.rect = self.image.get_rect(center=pos)
        self.mask = pygame.mask.from_surface(self.image)
        self.pos = Vector2(pos); self.vel = Vector2(0,0)
        self.nav_grid = nav_grid; self.cell_size = cell_size
        self.path = []; self.path_cells = []; self.path_idx = 0
        self.last_recalc = -9999.0; self.recalc_interval = PATH_RECALC_INTERVAL
        self.last_player_cell = None
        self.mode = 'chase'  # 'chase' (default) or 'flee' or 'halt'
        self.hit = False; self.hit_time = 0

    def request_path_to(self, player_pos, current_time):
        # compute path depending on mode
        pcx, pcy = world_to_cell(player_pos, self.cell_size)
        scx, scy = world_to_cell(self.pos, self.cell_size)
        now = current_time
        if (now - self.last_recalc) < self.recalc_interval:
            return
        self.last_recalc = now
        # choose goal cell based on mode
        rows = len(self.nav_grid); cols = len(self.nav_grid[0])
        if self.mode == 'chase':
            goal = (pcx, pcy)
        elif self.mode == 'flee':
            # attempt a mirrored cell away from player
            gx = scx + (scx - pcx)
            gy = scy + (scy - pcy)
            gx = max(0, min(cols-1, gx)); gy = max(0, min(rows-1, gy))
            goal = (gx, gy)
            if self.nav_grid[goal[1]][goal[0]] == 1:
                # fallback: choose a corner farthest from player among 4 corners
                corners = [(0,0),(cols-1,0),(0,rows-1),(cols-1,rows-1)]
                best = None; best_d = -1
                for c in corners:
                    cx, cy = c
                    if self.nav_grid[cy][cx] == 0:
                        d = math.hypot(cx - pcx, cy - pcy)
                        if d > best_d:
                            best_d = d; best = c
                if best:
                    goal = best
        else:
            return
        # clamp and ensure free
        gx, gy = goal
        if not (0 <= gx < cols and 0 <= gy < rows) or self.nav_grid[gy][gx] == 1:
            # search nearby free cell
            found = False
            for r in range(1,5):
                for dy in range(-r,r+1):
                    for dx in range(-r,r+1):
                        nx = gx + dx; ny = gy + dy
                        if 0 <= nx < cols and 0 <= ny < rows and self.nav_grid[ny][nx] == 0:
                            goal = (nx, ny); found = True; break
                    if found: break
                if found: break
            if not found:
                self.path = []; self.path_idx = 0; return
        path_cells = a_star(self.nav_grid, (scx, scy), goal)
        if not path_cells:
            self.path = []; self.path_idx = 0; return
        world_path = [cell_to_world_center(cx, cy, self.cell_size) for (cx, cy) in path_cells]
        compressed = []
        for i, pt in enumerate(world_path):
            if i == 0 or i == len(world_path)-1:
                compressed.append(pt); continue
            prev = world_path[i-1]; nxt = world_path[i+1]
            dir1 = (pt - prev); dir2 = (nxt - pt)
            if dir1.length_squared() == 0 or dir2.length_squared() == 0:
                compressed.append(pt); continue
            dir1 = dir1.normalize(); dir2 = dir2.normalize()
            if dir1.dot(dir2) < 0.999:
                compressed.append(pt)
        compressed.append(world_path[-1])
        self.path = compressed; self.path_idx = 0

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
        if now - self.last_frame_time >= dur:
            self.frame_idx = (self.frame_idx + 1) % len(self.current_frames)
            self.last_frame_time = now
            self.image = self.current_frames[self.frame_idx]
            self.mask = pygame.mask.from_surface(self.image)

    def update(self, dt, player, obstacles_group, all_enemies, current_time):
        # If already marked as hit, skip movement/logic; despawn handled externally.
        if self.hit:
            return

        # request path depending on current mode
        self.request_path_to(player.pos, current_time)

        # separation from other enemies
        sep = Vector2(0,0)
        for other in all_enemies:
            if other is self: continue
            d = self.pos.distance_to(other.pos)
            if d < SEPARATION_RADIUS and d > 0:
                away = (self.pos - other.pos) / (d*d)
                sep += away
        if sep.length_squared() > 0:
            sep = sep.normalize() * SEPARATION_FORCE * dt

        # obstacle avoidance (smooth steering, avoids hard padding pushes)
        avoid = Vector2(0,0)
        avoid_radius = max(self.cell_size * 0.8, 32)
        avoid_force = 600.0
        for ob in obstacles_group:
            ob_center = Vector2(ob.collision_rect.center)
            d = self.pos.distance_to(ob_center)
            if d < avoid_radius and d > 0:
                # stronger repulsion when closer; use inverse-square falloff
                repulse = (self.pos - ob_center) / (d * d)
                avoid += repulse
        if avoid.length_squared() > 0:
            avoid = avoid.normalize() * (avoid_force * dt)

        # path-following: compute desired velocity
        target_vel = Vector2(0,0)
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

        # steering: include separation and avoidance as velocity deltas
        steer = target_vel - self.vel
        steer += sep
        steer += avoid

        max_change = ENEMY_ACCELERATION * dt
        if steer.length() > max_change:
            steer = steer.normalize() * max_change
        self.vel += steer
        if self.vel.length() > ENEMY_MAX_SPEED:
            self.vel.scale_to_length(ENEMY_MAX_SPEED)

        # integrate with softer obstacle collision response (slide, don't teleport/push)
        next_pos = self.pos + self.vel * dt
        next_rect = self.rect.copy(); next_rect.center = (int(next_pos.x), int(next_pos.y))
        collided = False
        for ob in obstacles_group:
            if next_rect.colliderect(ob.collision_rect):
                off = (ob.collision_rect.left - next_rect.left, ob.collision_rect.top - next_rect.top)
                if self.mask.overlap(ob.collision_mask, off):
                    # Slide away gently instead of a hard teleport push
                    push = (self.pos - Vector2(ob.collision_rect.center))
                    if push.length_squared() == 0:
                        push = Vector2(random.uniform(-1,1), random.uniform(-1,1))
                    push = push.normalize() * (self.cell_size * 0.06)
                    # apply small displacement and damp velocity so enemy naturally steers away
                    self.pos += push
                    self.vel *= 0.55
                    collided = True
                    # invalidate current path so next update will recompute a better path
                    self.path = []
                    break
        if not collided:
            self.pos = next_pos
        self.rect.center = (int(self.pos.x), int(self.pos.y))
        self.update_animation()

# ------------------------------ placement utils ------------------------------

def place_obstacles(count, avoid_pos, min_dist, world_size, asset_pairs):
    obstacles = pygame.sprite.Group()
    attempts = 0; placed = 0; max_attempts = count * PLACEMENT_ATTEMPTS_MULT
    while placed < count and attempts < max_attempts:
        attempts += 1
        x = random.randint(64, world_size[0] - 64); y = random.randint(64, world_size[1] - 64)
        pos = Vector2(x,y)
        if pos.distance_to(Vector2(avoid_pos)) < min_dist: continue
        base_surf, top_surf = random.choice(asset_pairs)
        ob = Obstacle(base_surf, top_surf, pos)
        collide = False
        for e in obstacles:
            if ob.rect.colliderect(e.rect): collide = True; break
        if collide: continue
        obstacles.add(ob); placed += 1
    return obstacles


def place_enemies(count, avoid_pos, min_dist, world_size, nav_grid, cell_size, enemy_anims_list):
    enemies = pygame.sprite.Group()
    attempts = 0; placed = 0; max_attempts = count * PLACEMENT_ATTEMPTS_MULT
    while placed < count and attempts < max_attempts:
        attempts += 1
        x = random.randint(64, world_size[0] - 64); y = random.randint(64, world_size[1] - 64)
        pos = Vector2(x,y)
        if pos.distance_to(Vector2(avoid_pos)) < min_dist: continue
        too_close = False
        for en in enemies:
            if pos.distance_to(Vector2(en.rect.center)) < 70: too_close = True; break
        if too_close: continue
        anims = random.choice(enemy_anims_list)
        en = Enemy(pos, nav_grid, cell_size, anims, FRAME_DURATION)
        enemies.add(en); placed += 1
    return enemies

# ------------------------------ Main + Menu + Day/Night ------------------------------

def main():
    pygame.init()
    screen = pygame.display.set_mode(SCREEN_SIZE)
    pygame.display.set_caption('Top-down: 4-dir, A* enemies, Day/Night, Menu')
    clock = pygame.time.Clock()

    def load_image(path, fallback_size=(48,48)):
        if path and os.path.isfile(path):
            try:
                return pygame.image.load(path).convert_alpha()
            except Exception as e:
                print(f"Failed loading {path}: {e}")
        surf = pygame.Surface(fallback_size, pygame.SRCALPHA); surf.fill((180,180,180,255))
        pygame.draw.rect(surf, (0,0,0), surf.get_rect(), 2)
        return surf

    # build player animations
    player_anims = build_animations_from_master(MASTER_SHEET, FRAME_WIDTH, FRAME_HEIGHT, PLAYER_SHEET_LAYOUT, scale=SHEET_SCALE)
    player_start = (WORLD_SIZE[0]//2, WORLD_SIZE[1]//2)
    player = Player(player_anims, player_start, frame_durations=FRAME_DURATION)
    camera = Camera(SCREEN_SIZE, WORLD_SIZE)

    # load obstacles
    tree_base = load_image(os.path.join(ASSET_DIR, 'obstacles', 'treebase.png'))
    tree_top  = load_image(os.path.join(ASSET_DIR, 'obstacles', 'treetop.png'))
    rock_base = load_image(os.path.join(ASSET_DIR, 'obstacles', 'rock.png'))
    rock_top  = None
    OBSTACLE_ASSET_PAIRS = [(tree_base, tree_top), (rock_base, rock_top)]
    obstacles = place_obstacles(OBSTACLE_COUNT, player_start, OBSTACLE_MIN_DIST, WORLD_SIZE, OBSTACLE_ASSET_PAIRS)

    # build nav grid
    nav_grid = build_nav_grid(WORLD_SIZE, NAV_CELL_SIZE, obstacles, expand_cells=NAV_EXPAND_CELLS)

    # discover enemy sprite sheets
    enemy_anims_list = []
    if os.path.isdir(ENEMY_SPRITES_DIR):
        for f in os.listdir(ENEMY_SPRITES_DIR):
            if f.lower().endswith('.png'):
                path = os.path.join(ENEMY_SPRITES_DIR, f)
                anims = build_animations_from_master(path, FRAME_WIDTH, FRAME_HEIGHT, ENEMY_SHEET_LAYOUT, scale=SHEET_SCALE)
                enemy_anims_list.append(anims)
    if not enemy_anims_list:
        surf = pygame.Surface((36,36), pygame.SRCALPHA); pygame.draw.circle(surf, (160,40,40), (18,18), 18)
        anims = {'idle':{}, 'run':{}}
        for d in ['down','left','right','up']:
            anims['idle'][d] = [surf]; anims['run'][d] = [surf]
        enemy_anims_list.append(anims)

    enemies = place_enemies(ENEMY_COUNT, player_start, ENEMY_SPAWN_MIN_DIST, WORLD_SIZE, nav_grid, NAV_CELL_SIZE, enemy_anims_list)

    # heart UI
    heart_img = None
    if os.path.isfile(HEART_IMG):
        heart_img = load_image(HEART_IMG)
        if heart_img.get_height() > 48:
            scale = 48 / heart_img.get_height(); heart_img = pygame.transform.scale(heart_img, (int(heart_img.get_width()*scale), 48))
    else:
        heart_img = pygame.Surface((36,36), pygame.SRCALPHA)
        pygame.draw.polygon(heart_img, (220,50,50), [(18,4),(30,12),(18,32),(6,12)])
        pygame.draw.circle(heart_img, (220,50,50), (11,10), 6)
        pygame.draw.circle(heart_img, (220,50,50), (25,10), 6)

    menu_bg = load_image(MENU_BG, fallback_size=SCREEN_SIZE)
    win_img = load_image(WIN_IMG, fallback_size=(400,200))

    font = pygame.font.SysFont(None, 28)

    # menu layout
    start_btn = pygame.Rect((SCREEN_SIZE[0]//2 - 80, SCREEN_SIZE[1]//2 + 40, 160, 48))

    # day/night state
    game_state = 'menu'  # 'menu', 'playing', 'won'
    day_timer = 0.0
    is_night = False
    night_phase = 'none'  # 'none', 'idle_halt', 'flee'
    night_phase_timer = 0.0

    last_player_pos_for_repath = Vector2(player.pos)
    running = True
    while running:
        dt = clock.tick(FPS) / 1000.0
        now_ms = pygame.time.get_ticks()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                if game_state == 'menu': running = False
                else: game_state = 'menu'
            elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                mx, my = event.pos
                if game_state == 'menu':
                    if start_btn.collidepoint(mx, my):
                        # start the game
                        # reset world & player
                        player = Player(player_anims, player_start, frame_durations=FRAME_DURATION)
                        obstacles = place_obstacles(OBSTACLE_COUNT, player_start, OBSTACLE_MIN_DIST, WORLD_SIZE, OBSTACLE_ASSET_PAIRS)
                        nav_grid = build_nav_grid(WORLD_SIZE, NAV_CELL_SIZE, obstacles, expand_cells=NAV_EXPAND_CELLS)
                        enemies = place_enemies(ENEMY_COUNT, player_start, ENEMY_SPAWN_MIN_DIST, WORLD_SIZE, nav_grid, NAV_CELL_SIZE, enemy_anims_list)
                        day_timer = 0.0; is_night = False; night_phase = 'none'; night_phase_timer = 0.0
                        game_state = 'playing'
                elif game_state == 'won':
                    # clicking anywhere returns to menu (simple UX)
                    game_state = 'menu'

        keys = pygame.key.get_pressed()

        if game_state == 'menu':
            # draw menu
            screen.fill((30,30,30))
            screen.blit(menu_bg, (0,0))
            # start button
            pygame.draw.rect(screen, (60,160,60), start_btn)
            txt = font.render('START', True, (255,255,255))
            screen.blit(txt, (start_btn.centerx - txt.get_width()//2, start_btn.centery - txt.get_height()//2))
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
            # transition into night
            if is_night and not was_night:
                # night just started: set phase to idle_halt
                night_phase = 'idle_halt'; night_phase_timer = NIGHT_IDLE_MS / 1000.0
                # pause player control and enemies
                player.pause_until = pygame.time.get_ticks() + NIGHT_IDLE_MS
                for en in enemies:
                    en.mode = 'halt'
                # optionally set player to 'night' state for animation
                player.state = 'night'
                player.frame_idx = 0
                player.last_frame_time = pygame.time.get_ticks()
            # during night phases
            if is_night:
                if night_phase == 'idle_halt':
                    night_phase_timer -= dt
                    if night_phase_timer <= 0:
                        night_phase = 'flee'
                        # make enemies flee and recalc paths
                        for en in enemies:
                            en.mode = 'flee'
                            en.last_recalc = -9999.0
                elif night_phase == 'flee':
                    # enemies flee for rest of night; player control resumes
                    player.state = 'idle'  # ensure normal animation for movement
            else:
                # day: enemies chase
                if night_phase != 'none':
                    night_phase = 'none'
                    for en in enemies:
                        en.mode = 'chase'
                        en.last_recalc = -9999.0

            # Update player (allow control unless in pause/freeze)
            player.update(dt, keys, allow_control=True)

            # Player vs obstacles
            for ob in obstacles:
                if player.rect.colliderect(ob.collision_rect):
                    offset = (ob.collision_rect.left - player.rect.left, ob.collision_rect.top - player.rect.top)
                    if player.mask.overlap(ob.collision_mask, offset):
                        player.collide_with_obstacle(ob)
                        break

            # Update enemies
            now_sec = pygame.time.get_ticks() / 1000.0
            for en in list(enemies):
                # if hit, check despawn and award heart on actual despawn
                if en.hit:
                    if pygame.time.get_ticks() - en.hit_time >= ENEMY_DESPAWN_MS:
                        # award heart to player when enemy actually despawns
                        player.hearts = min(99, player.hearts + 1)
                        enemies.remove(en)
                    continue
                # if halted, skip movement
                if en.mode == 'halt':
                    continue
                en.update(dt, player, obstacles, enemies, now_sec)

            # Enemy-player collision
            for en in list(enemies):
                if en.rect.colliderect(player.rect):
                    offset = (en.rect.left - player.rect.left, en.rect.top - player.rect.top)
                    if player.mask.overlap(en.mask, offset):
                        # behavior changes depending on current night_phase
                        if is_night and night_phase == 'flee':
                            # player caught fleeing enemy -> mark enemy to be despawned; award heart only when it despawns
                            player.pause_until = pygame.time.get_ticks() + PLAYER_PAUSE_ON_CATCH_MS
                            en.hit = True
                            en.hit_time = pygame.time.get_ticks()
                            # flag that this enemy will grant a heart when despawned (handled in despawn logic)
                            # (no immediate heart increment)
                        else:
                            # normal daytime collision: knockback + lose heart (original behaviour)
                            player.hearts = max(0, player.hearts - 1)
                            player.hit_by_enemy(en)
                            en.vel *= -0.3
                        break

            # camera
            camera.update(player.rect)

            # draw world
            screen.fill((102,170,255))
            ground_rect = pygame.Rect(-int(camera.offset.x), -int(camera.offset.y), WORLD_SIZE[0], WORLD_SIZE[1])
            pygame.draw.rect(screen, (30,120,30), ground_rect)

            # draw base obstacles
            for ob in obstacles:
                screen.blit(ob.base_image, camera.apply(ob.collision_rect).topleft)

            # draw enemies (y-sort); apply red overlay if hit
            for en in sorted(enemies, key=lambda e: e.pos.y):
                img = en.image.copy()
                if en.hit:
                    overlay = pygame.Surface(img.get_size(), pygame.SRCALPHA)
                    overlay.fill((255, 0, 0, 140))
                    img.blit(overlay, (0,0), special_flags=pygame.BLEND_RGBA_ADD)
                screen.blit(img, camera.apply(en.rect).topleft)

            # draw player with flash
            player_draw_img = player.image.copy()
            if pygame.time.get_ticks() < player.flash_until:
                overlay = pygame.Surface(player_draw_img.get_size(), pygame.SRCALPHA)
                overlay.fill((255,0,0,100))
                player_draw_img.blit(overlay, (0,0), special_flags=pygame.BLEND_RGBA_ADD)
            screen.blit(player_draw_img, camera.apply(player.rect).topleft)

            # draw top parts
            for ob in obstacles:
                if ob.top_image:
                    screen.blit(ob.top_image, camera.apply(ob.top_rect).topleft)

            # night darkness overlay
            if is_night:
                dark = pygame.Surface(SCREEN_SIZE, pygame.SRCALPHA)
                dark.fill((0,0,0,DARK_ALPHA))
                screen.blit(dark, (0,0))

            # UI: hearts
            padding = 8
            for i in range(player.hearts):
                x = padding + i * (heart_img.get_width() + 4); y = padding
                screen.blit(heart_img, (x, y))

            # UI: stamina bar
            bar_w = 160; bar_h = 14
            bar_x = SCREEN_SIZE[0] - bar_w - 12; bar_y = 12
            pygame.draw.rect(screen, (40,40,40), (bar_x, bar_y, bar_w, bar_h))
            perc = player.stamina / STAMINA_MAX; inner_w = int(bar_w * perc)
            pygame.draw.rect(screen, (80,200,120), (bar_x+2, bar_y+2, max(0, inner_w-4), bar_h-4))
            stext = font.render(f"Stamina", True, (255,255,255)); screen.blit(stext, (bar_x - 86, bar_y - 2))

            # check win
            if len(enemies) == 0:
                game_state = 'won'
            pygame.display.flip()
            continue

        if game_state == 'won':
            screen.fill((0,0,0))
            # center win image
            win_rect = win_img.get_rect(center=(SCREEN_SIZE[0]//2, SCREEN_SIZE[1]//2 - 40))
            screen.blit(win_img, win_rect.topleft)
            msg = font.render('You won! Click anywhere to return to menu', True, (255,255,255))
            screen.blit(msg, ((SCREEN_SIZE[0] - msg.get_width())//2, win_rect.bottom + 8))
            pygame.display.flip()
            continue

    pygame.quit()

if __name__ == '__main__':
    main()


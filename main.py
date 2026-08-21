import sys
import pygame
import math
import random
import threading
import asyncio

IS_BROWSER = sys.platform == "emscripten"

try:
    import websockets
    from websockets.sync.client import connect
except ModuleNotFoundError:
    websockets = None
    connect = None

# Initialize Pygame pygame.init()
pygame.init()






# Window Setup
WIDTH, HEIGHT = (1280, 720) if IS_BROWSER else (800, 600)
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("War of earth")
clock = pygame.time.Clock()

# Change SysFont to default:
font = pygame.font.Font(None, 24)
mini_font = pygame.font.Font(None, 18)
large_font = pygame.font.Font(None, 48)


# --- MAP CONFIGURATIONS ---
TILE_SIZE = 64

# Map 1: Original Tech Room
MAP_TECH = [
    [1, 1, 1, 1, 1, 1, 1, 1],
    [1, 0, 0, 0, 0, 0, 0, 1],
    [1, 0, 2, 0, 0, 2, 0, 1],
    [1, 0, 0, 0, 0, 0, 0, 1],
    [1, 0, 0, 0, 0, 0, 0, 1],
    [1, 0, 2, 0, 0, 2, 0, 1],
    [1, 0, 0, 0, 0, 0, 0, 1],
    [1, 1, 1, 1, 1, 1, 1, 1],
]

# Map 2: Neighborhood Layout (Expanded 18x15 Grid)
MAP_NEIGHBORHOOD = [
    [3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3],
    [3, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 3],
    [3, 4, 4, 5, 4, 0, 0, 3, 3, 5, 3, 3, 0, 4, 4, 4, 0, 3],
    [3, 4, 0, 0, 4, 0, 0, 3, 0, 0, 0, 3, 0, 4, 0, 4, 0, 3],
    [3, 4, 4, 4, 4, 0, 0, 3, 3, 3, 3, 3, 0, 5, 0, 4, 0, 3],
    [3, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 4, 0, 4, 0, 3],
    [3, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 4, 4, 4, 0, 3],
    [3, 3, 5, 3, 3, 0, 0, 4, 4, 5, 4, 3, 0, 0, 0, 0, 0, 3],
    [3, 3, 0, 0, 3, 0, 0, 4, 0, 0, 4, 3, 0, 3, 3, 5, 3, 3],
    [3, 3, 0, 0, 3, 0, 0, 4, 4, 4, 4, 3, 0, 3, 0, 0, 0, 3],
    [3, 3, 3, 3, 3, 0, 0, 0, 0, 0, 0, 0, 0, 3, 0, 0, 0, 3],
    [3, 0, 0, 0, 0, 0, 0, 4, 4, 5, 4, 4, 0, 3, 3, 3, 3, 3],
    [3, 0, 4, 4, 5, 4, 0, 4, 0, 0, 0, 4, 0, 0, 0, 0, 0, 3],
    [3, 0, 4, 4, 4, 4, 0, 4, 4, 4, 4, 4, 0, 0, 0, 0, 0, 3],
    [3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3],
]

# Map 3: Soccer Field Layout (6 = Stadium Concrete Wall, 7 = Goal Posts)
MAP_SOCCER = [
    [6, 6, 6, 6, 6, 6, 6, 6, 6, 6, 6, 6, 6, 6],
    [6, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 6],
    [6, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 6],
    [6, 7, 7, 0, 0, 0, 0, 0, 0, 0, 0, 7, 7, 6],
    [6, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 6],
    [6, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 6],
    [6, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 6],
    [6, 7, 7, 0, 0, 0, 0, 0, 0, 0, 0, 7, 7, 6],
    [6, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 6],
    [6, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 6,],
    [6, 6, 6, 6, 6, 6, 6, 6, 6, 6, 6, 6, 6, 6],
]

# Map 4: Space Station (8 = Steel Airship Hull, 9 = Neon Energy Shield Wall)
MAP_SPACE_STATION = [
    [8, 8, 8, 8, 8, 8, 8, 8, 8, 8, 8, 8, 8, 8, 8, 8],
    [8, 0, 0, 0, 8, 0, 0, 0, 0, 0, 0, 8, 0, 0, 0, 8],
    [8, 0, 9, 0, 8, 0, 8, 8, 8, 8, 0, 8, 0, 9, 0, 8],
    [8, 0, 0, 0, 5, 0, 8, 0, 0, 8, 0, 5, 0, 0, 0, 8],
    [8, 8, 5, 8, 8, 0, 8, 0, 0, 8, 0, 8, 8, 5, 8, 8],
    [8, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 8],
    [8, 0, 8, 8, 8, 0, 8, 9, 9, 8, 0, 8, 8, 8, 0, 8],
    [8, 0, 8, 0, 0, 0, 8, 0, 0, 8, 0, 0, 0, 8, 0, 8],
    [8, 0, 8, 0, 9, 0, 5, 0, 0, 5, 0, 9, 0, 8, 0, 8],
    [8, 0, 8, 8, 8, 8, 8, 8, 8, 8, 8, 8, 8, 8, 0, 8],
    [8, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 8],
    [8, 8, 8, 8, 8, 8, 8, 8, 8, 8, 8, 8, 8, 8, 8, 8],
]

active_map = MAP_TECH
map_name = "TECH ROOM"
map_size_y = len(active_map)
map_size_x = len(active_map[0])

# Player Setup
player_x = 3.5 * TILE_SIZE  
player_y = 5.0 * TILE_SIZE  
player_angle = -math.pi / 2  
FOV = math.pi / 3  
HALF_FOV = FOV / 2
NUM_RAYS = 160  
max_rays_render = 80 if IS_BROWSER else NUM_RAYS
DELTA_ANGLE = FOV / NUM_RAYS
MAX_DEPTH = 600 if IS_BROWSER else 1000
SCALE = WIDTH // NUM_RAYS

# Health & State Parameters
player_hp = 100
player_max_hp = 100
player_alive = True
AIM_ANGLE_THRESHOLD = math.radians(60)
MAX_SHOT_DISTANCE = 500
CROSSHAIR_SIZE = 8

# Jump Variables
player_z = 0         
jump_velocity = 0     
gravity = 0.6         
is_jumping = False

# --- PALETTES ---
BLACK = (5, 5, 10)
MATRIX_GREEN = (0, 255, 140)
TECH_CYAN = (0, 180, 255)
DARK_CORE = (10, 12, 22)
ROOF_BEAM = (0, 60, 90)
FLOOR_GRID = (0, 40, 60)
WHITE = (255, 255, 255)

# Neighborhood / Soccer Palettes
SKY_BLUE = (90, 155, 230)
SKY_HORIZON = (180, 215, 255)
GRASS_GREEN = (45, 120, 55)
SOCCER_PITCH_GREEN = (34, 139, 34)
ASPHALT_ROAD = (50, 52, 58)
BRICK_RED = (145, 45, 35)
HOUSE_BROWN = (110, 80, 60)
WINDOW_BLUE = (25, 65, 110)
STADIUM_WHITE = (220, 225, 230)
GOAL_YELLOW = (230, 180, 30)

# Weapon and Skin Colors
GUN_STEEL = (60, 65, 70)
GUN_DARK = (25, 28, 32)
GUN_METAL = (45, 48, 52)
SLEEVE_COLOR = (25, 30, 40)
SKIN_BASE = (229, 175, 142)
SKIN_SHADOW = (163, 109, 80)
SKIN_HIGH = (248, 207, 181)
SKIN_NAIL = (222, 178, 170)
SKIN_DARK_SHADOW = (110, 68, 44)

# --- ADVANCED PROCEDURAL TEXTURE GENERATION SYSTEM ---
TEX_SIZE = 64
def generate_textures():
    tex_dict = {}

    # 3: Ultra Realistic Brick Texture
    brick = pygame.Surface((TEX_SIZE, TEX_SIZE))
    for y in range(TEX_SIZE):

        for x in range(TEX_SIZE):
            row = y // 8
            is_mortar = (y % 8 == 0) or ((x + (4 if row % 2 == 0 else 0)) % 16 == 0)
            if is_mortar:
                brick.set_at((x, y), (170, 175, 180)) 
            else:
                noise = random.randint(-15, 15)
                brick.set_at((x, y), (max(0, min(255, BRICK_RED[0] + noise)), 
                                      max(0, min(255, BRICK_RED[1] + noise // 2)), 
                                      max(0, min(255, BRICK_RED[2] + noise // 3))))
    tex_dict[3] = brick

    # 4: Wood Siding
    wood = pygame.Surface((TEX_SIZE, TEX_SIZE))
    for y in range(TEX_SIZE):

        for x in range(TEX_SIZE):
            is_seam = (y % 16 == 0)
            if is_seam:
                wood.set_at((x, y), (40, 28, 20)) 
            else:
                grain = random.randint(-8, 8) + int(math.sin(x * 0.5) * 4)
                wood.set_at((x, y), (max(0, min(255, HOUSE_BROWN[0] + grain)), 
                                     max(0, min(255, HOUSE_BROWN[1] + grain)), 
                                     max(0, min(255, HOUSE_BROWN[2] + grain))))
    tex_dict[4] = wood

    # 5: Panelled Wood Door
    door = pygame.Surface((TEX_SIZE, TEX_SIZE))
    for y in range(TEX_SIZE):

        for x in range(TEX_SIZE):
            grain = random.randint(-6, 6)
            base_r, base_g, base_b = 100 + grain, 75 + grain, 60 + grain
            if (6 < x < 26 or 38 < x < 58) and (6 < y < 26 or 34 < y < 54):
                if x == 7 or x == 25 or y == 7 or y == 25 or x == 39 or x == 57 or y == 34 or y == 54:
                    base_r, base_g, base_b = 45, 30, 20 
                else:
                    base_r, base_g, base_b = base_r + 15, base_g + 10, base_b + 5
            door.set_at((x, y), (max(0, min(255, base_r)), max(0, min(255, base_g)), max(0, min(255, base_b))))
    tex_dict[5] = door

    # 6: Concrete Wall Texture
    concrete = pygame.Surface((TEX_SIZE, TEX_SIZE))
    for y in range(TEX_SIZE):

        for x in range(TEX_SIZE):
            c_noise = random.randint(-12, 12)
            concrete.set_at((x, y), (max(0, min(255, STADIUM_WHITE[0] + c_noise)), 
                                     max(0, min(255, STADIUM_WHITE[1] + c_noise)), 
                                     max(0, min(255, STADIUM_WHITE[2] + c_noise))))
    tex_dict[6] = concrete

    # 7: Goal Posts
    goal = pygame.Surface((TEX_SIZE, TEX_SIZE))
    for y in range(TEX_SIZE):

        for x in range(TEX_SIZE):
            if (x // 8) % 2 == 0:
                goal.set_at((x, y), GOAL_YELLOW)
            else:
                goal.set_at((x, y), (240, 240, 245))
    tex_dict[7] = goal

    # 8: Steel Space Station Hull
    hull = pygame.Surface((TEX_SIZE, TEX_SIZE))
    for y in range(TEX_SIZE):

        for x in range(TEX_SIZE):
            is_seam = (x % 16 == 0) or (y % 16 == 0)
            if is_seam:
                hull.set_at((x, y), (20, 25, 35))
            else:
                noise = random.randint(-10, 10)
                hull.set_at((x, y), (max(0, min(255, 110 + noise)), 
                                     max(0, min(255, 120 + noise)), 
                                     max(0, min(255, 135 + noise))))
    tex_dict[8] = hull

    # 9: Neon Energy Shield Wall
    shield = pygame.Surface((TEX_SIZE, TEX_SIZE))
    for y in range(TEX_SIZE):

        for x in range(TEX_SIZE):
            grid_line = (x % 8 == 0) or (y % 8 == 0)
            if grid_line:
                shield.set_at((x, y), (0, 240, 255))
            else:
                shield.set_at((x, y), (10, 20, 50))
    tex_dict[9] = shield

    return tex_dict

TEXTURES = generate_textures()

# -- OPTICAL ENGINE: POST-PROCESS MASK CREATION --
# Creates a physical overlay simulation of lens vignetting to darken corner bounds
VIGNETTE_MASK = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
for y in range(HEIGHT):
    for x in range(WIDTH):
        dx = (x - WIDTH // 2) / (WIDTH // 2)
        dy = (y - HEIGHT // 2) / (HEIGHT // 2)
        dist = math.sqrt(dx * dx + dy * dy)
        if dist > 0.4:
            alpha = int(min(185, (dist - 0.4) * 240))
            VIGNETTE_MASK.set_at((x, y), (0, 0, 0, alpha))
# --- NETWORKING GLOBALS ---
SERVER_IP = "127.0.0.1"
PORT = 5555

client_socket = None
is_searching = False
online_mode = False
match_trigger_received = False
player_hp = 100
player_alive = True
network_players = []

# --- STATE MANAGEMENT ---
game_state = "MENU"
has_gun = False
gun_world_x = 3.5 * TILE_SIZE
gun_world_y = 3.5 * TILE_SIZE

start_btn_rect = pygame.Rect(WIDTH // 2 - 100, HEIGHT // 2 + 30, 200, 50)
tick_counter = 0

btn_online_rect = pygame.Rect(WIDTH // 2 - 180, HEIGHT // 2 - 30, 360, 50)
btn_npcs_rect = pygame.Rect(WIDTH // 2 - 180, HEIGHT // 2 + 50, 360, 50)

btn_map_neighborhood = pygame.Rect(WIDTH // 2 - 220, HEIGHT // 2 - 70, 440, 45)
btn_map_soccer       = pygame.Rect(WIDTH // 2 - 220, HEIGHT // 2 - 15, 440, 45)
btn_map_space        = pygame.Rect(WIDTH // 2 - 220, HEIGHT // 2 + 40, 440, 45)

is_shooting = False
shoot_frame = 0
recoil_offset_y = 0
muzzle_flash_timer = 0
laser_beams = []  

class NPC:
    def __init__(self, x, y, hp):
        self.x = x
        self.y = y
        self.max_hp = hp
        self.hp = hp
        self.alive = True
        self.flash_timer = 0

active_npcs = [NPC(3.5 * TILE_SIZE, 2.0 * TILE_SIZE, 25)]
network_players = [] 

def listen_to_server():
    global client_socket, match_trigger_received, player_hp, player_alive
    if connect is None or websockets is None:
        return
    try:
        while online_mode and client_socket:
            response = client_socket.recv()  # Receives WebSocket text directly
            if response.startswith("MATCH_START"):
                match_trigger_received = True
                player_hp = 100
                player_alive = True
            elif response.startswith("MOVE:"):
                _, ox, oy = response.split(":")
                if network_players:
                    network_players[0].x = float(ox)
                    network_players[0].y = float(oy)
            elif response.startswith("DAMAGE:"):
                _, dmg_amount = response.split(":")
                player_hp = max(0, player_hp - int(dmg_amount))
                if player_hp == 0:
                    player_alive = False
    except Exception:
        pass


def start_matchmaking_connection():
    global client_socket, is_searching, online_mode
    if connect is None or websockets is None:
        client_socket = None
        is_searching = False
        online_mode = False
        return
    try:
        client_socket = connect(f"ws://{SERVER_IP}:{PORT}")
        is_searching = True
        online_mode = True
        client_socket.send("JOIN_QUEUE")
        threading.Thread(target=listen_to_server, daemon=True).start()
    except Exception:
        client_socket = None
        is_searching = False
        online_mode = False


def send_my_position():
    global client_socket
    if online_mode and client_socket and connect is not None and websockets is not None:
        try:
            client_socket.send(f"MOVE:{player_x}:{player_y}")
        except Exception:
            pass

def draw_tapered_finger(surface, base_x, base_y, length, angle, thickness, base_color, shadow_color, mirror=False):
    rad = math.radians(angle) if not mirror else math.radians(180 - angle)
    mid_x = base_x + int(length * 0.55 * math.cos(rad))
    mid_y = base_y - int(length * 0.55 * math.sin(rad))
    tip_x = base_x + int(length * math.cos(rad))
    tip_y = base_y - int(length * math.sin(rad))

    t1 = thickness
    t2 = int(thickness * 0.75)
    t3 = int(thickness * 0.5)
    perp = rad + math.pi/2

    p1 = (int(base_x + t1*math.cos(perp)), int(base_y - t1*math.sin(perp)))
    p2 = (int(mid_x + t2*math.cos(perp)), int(mid_y - t2*math.sin(perp)))
    p3 = (int(tip_x + t3*math.cos(perp)), int(tip_y - t3*math.sin(perp)))
    p4 = (int(tip_x - t3*math.cos(perp)), int(tip_y - t3*math.sin(perp)))
    p5 = (int(mid_x - t2*math.cos(perp)), int(mid_y - t2*math.sin(perp)))
    p6 = (int(base_x - t1*math.cos(perp)), int(base_y - t1*math.sin(perp)))

    try:
        pygame.draw.polygon(surface, shadow_color, [p1, p2, p3, p4, p5, p6])
        p1_in = (int(base_x + (t1-1)*math.cos(perp)), int(base_y - (t1-1)*math.sin(perp)))
        p3_in = (int(tip_x + (t3-1)*math.cos(perp)), int(tip_y - (t3-1)*math.sin(perp)))
        p4_in = (int(tip_x - (t3-1)*math.cos(perp)), int(tip_y - (t3-1)*math.sin(perp)))
        p6_in = (int(base_x - (t1-1)*math.cos(perp)), int(base_y - (t1-1)*math.sin(perp)))
        pygame.draw.polygon(surface, base_color, [p1_in, p3_in, p4_in, p6_in])

        nail_size = max(2, t3 - 1)
        pygame.draw.circle(surface, SKIN_NAIL, (int(tip_x - (2 if not mirror else -2)*math.cos(rad)), int(tip_y + (2*math.sin(rad)))), nail_size)
    except:
        pass

def fire_weapon():
    global is_shooting, shoot_frame, muzzle_flash_timer
    if has_gun and not is_shooting and player_alive:
        is_shooting = True
        shoot_frame = 0
        muzzle_flash_timer = 5  
        laser_beams.append({'age': 0, 'max_age': 15})

        targets = active_npcs if not online_mode or game_state == "GAMEPLAY" else network_players

        for target in targets:
            if not target.alive: 
                continue

            # 1. Calculate relative distance and vector to target
            vec_x = target.x - player_x
            vec_y = target.y - player_y
            dist = math.hypot(vec_x, vec_y)

            if dist == 0:
                continue

            # 2. Normalize target angle relative to player view
            target_angle = math.atan2(vec_y, vec_x)
            diff_angle = target_angle - player_angle

            # Normalize angle to range (-pi, pi)
            diff_angle = (diff_angle + math.pi) % (2 * math.pi) - math.pi

            # 3. Check if target is inside the aim cone. This is intentionally forgiving so
            # a normal click while the NPC is in front of the player still registers damage.
            if dist <= MAX_SHOT_DISTANCE and abs(diff_angle) < AIM_ANGLE_THRESHOLD:
                blocked = False
                check_dist = 0

                # Step along line of sight to check for walls
                while check_dist < dist - 20: # Stop right before hitting target center
                    cx = player_x + check_dist * math.cos(player_angle)
                    cy = player_y + check_dist * math.sin(player_angle)
                    grid_x = int(cx / TILE_SIZE)
                    grid_y = int(cy / TILE_SIZE)

                    if 0 <= grid_x < map_size_x and 0 <= grid_y < map_size_y:
                        if active_map[grid_y][grid_x] > 0:
                            blocked = True
                            break
                    check_dist += 10

                # 4. Apply damage if not blocked by a wall
                if not blocked:
                    if not online_mode or game_state == "GAMEPLAY":
                        target.hp = max(0, target.hp - 25)
                        target.flash_timer = 6
                        if target.hp <= 0:
                            target.alive = False
                    else:
                        if online_mode and client_socket:
                            try:
                                client_socket.send("SHOT_HIT:500".encode('utf-8'))
                            except:
                                pass

def select_and_load_map(chosen_map):
    global active_map, map_name, map_size_x, map_size_y, player_x, player_y, active_npcs, network_players, game_state
    if chosen_map == "NEIGHBORHOOD":
        active_map = MAP_NEIGHBORHOOD
        map_name = "NEIGHBORHOOD"
        player_x, player_y = 1.5 * TILE_SIZE, 1.5 * TILE_SIZE
        if online_mode:
            network_players = [NPC(5.5 * TILE_SIZE, 1.5 * TILE_SIZE, 100)]
            active_npcs = []
        else:
            active_npcs = [
                NPC(5.5 * TILE_SIZE, 1.5 * TILE_SIZE, 300),
                NPC(2.5 * TILE_SIZE, 9.5 * TILE_SIZE, 300),
                NPC(10.5 * TILE_SIZE, 4.5 * TILE_SIZE, 300)
            ]
            network_players = []
    elif chosen_map == "SOCCER":
        active_map = MAP_SOCCER
        map_name = "SOCCER STADIUM"
        player_x, player_y = 2.5 * TILE_SIZE, 5.0 * TILE_SIZE
        if online_mode:
            network_players = [NPC(9.5 * TILE_SIZE, 5.0 * TILE_SIZE, 100)]
            active_npcs = []
    elif chosen_map == "SPACE":
            active_map = MAP_SPACE_STATION
            map_name = "DEEP SPACE STATION"
            player_x, player_y = 1.5 * TILE_SIZE, 1.5 * TILE_SIZE
            if online_mode:
                network_players = [NPC(14.5 * TILE_SIZE, 10.5 * TILE_SIZE, 100)]
                active_npcs = []
            else:
                active_npcs = [
                    NPC(7.5 * TILE_SIZE, 5.5 * TILE_SIZE, 25),
                    NPC(14.5 * TILE_SIZE, 1.5 * TILE_SIZE, 25),
                    NPC(14.5 * TILE_SIZE, 10.5 * TILE_SIZE, 25)
                ]
                network_players = []


    map_size_y = len(active_map)
    map_size_x = len(active_map[0])
    game_state = "GAMEPLAY" 
async def main():
    global game_state, is_searching, online_mode, match_trigger_received
    global player_x, player_y, player_angle, player_z, jump_velocity, is_jumping
    global player_hp, player_alive, has_gun, is_shooting, shoot_frame
    global recoil_offset_y, muzzle_flash_timer, tick_counter
    global active_npcs, network_players, client_socket
    running = True
    while running:
        tick_counter += 1
        mouse_pos = pygame.mouse.get_pos()

        if match_trigger_received:
            match_trigger_received = False
            is_searching = False
            game_state = "MAP_SELECT"

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            if event.type == pygame.MOUSEBUTTONDOWN:
                if game_state == "MENU":
                    if start_btn_rect.collidepoint(mouse_pos):
                        active_npcs = [NPC(3.5 * TILE_SIZE, 2.0 * TILE_SIZE, 500)]
                        has_gun = False
                        player_hp = 100
                        player_alive = True
                        game_state = "GAMEPLAY"

                elif game_state == "LOBBY" and not is_searching:
                    if btn_online_rect.collidepoint(mouse_pos):
                        online_mode = True
                        start_matchmaking_connection()

                    elif btn_npcs_rect.collidepoint(mouse_pos):
                        online_mode = False
                        game_state = "MAP_SELECT"

                elif game_state == "MAP_SELECT":
                    if btn_map_neighborhood.collidepoint(mouse_pos):
                        select_and_load_map("NEIGHBORHOOD")
                    elif btn_map_soccer.collidepoint(mouse_pos):
                        select_and_load_map("SOCCER")
                    elif btn_map_space.collidepoint(mouse_pos):
                      select_and_load_map("SPACE")

                elif game_state in ["GAMEPLAY", "NEIGHBORHOOD"]:
                    if event.button == 1:  
                        fire_weapon()

            if event.type == pygame.KEYDOWN and game_state in ["GAMEPLAY", "NEIGHBORHOOD"]:
                if event.key == pygame.K_j and not is_jumping and player_alive:
                    is_jumping = True
                    jump_velocity = 10  

                if event.key == pygame.K_SPACE:
                    fire_weapon()

                # --- DOOR INTERACTION LOGIC ---
                # Press 'E' to open doors (tile index 5)
                if event.key == pygame.K_e and player_alive:
                    interact_dist = 1.5 * TILE_SIZE
                    for d in range(0, int(interact_dist), 4):
                        target_x = player_x + d * math.cos(player_angle)
                        target_y = player_y + d * math.sin(player_angle)
                        col = int(target_x / TILE_SIZE)
                        row = int(target_y / TILE_SIZE)
                        if 0 <= col < map_size_x and 0 <= row < map_size_y:
                            if active_map[row][col] == 5:  # It's a closed wooden door
                                active_map[row][col] = 0   # Open the door (set to walkable space)
                                break

        keys = pygame.key.get_pressed()
        speed = 4
        rot_speed = 0.05

        if game_state in ["GAMEPLAY", "NEIGHBORHOOD"] and keys[pygame.K_ESCAPE]:
            game_state = "MENU"
            has_gun = False
            player_hp = 100
            player_alive = True
            player_x = 3.5 * TILE_SIZE
            player_y = 5.0 * TILE_SIZE
            player_angle = -math.pi / 2
            player_z = 0
            jump_velocity = 0
            is_jumping = False
            active_npcs = [NPC(3.5 * TILE_SIZE, 2.0 * TILE_SIZE, 25)]
            network_players = []
            is_searching = False
            online_mode = False
            client_socket = None
            match_trigger_received = False

        if game_state in ["GAMEPLAY", "NEIGHBORHOOD"]:
            if player_alive:
                if is_jumping:
                    player_z += jump_velocity
                    jump_velocity -= gravity
                    if player_z <= 0:  
                        player_z = 0
                        jump_velocity = 0
                        is_jumping = False

                if keys[pygame.K_LEFT] or keys[pygame.K_a]: player_angle -= rot_speed
                if keys[pygame.K_RIGHT] or keys[pygame.K_d]: player_angle += rot_speed

                move_x = 0
                move_y = 0
                if keys[pygame.K_UP] or keys[pygame.K_w]:
                    move_x += math.cos(player_angle) * speed
                    move_y += math.sin(player_angle) * speed
                if keys[pygame.K_DOWN] or keys[pygame.K_s]:
                    move_x -= math.cos(player_angle) * speed
                    move_y -= math.sin(player_angle) * speed

                new_x = player_x + move_x
                new_y = player_y + move_y
                buffer = 15
                cx_plus = new_x + (buffer if move_x > 0 else -buffer)
                cy_plus = new_y + (buffer if move_y > 0 else -buffer)

                targets = active_npcs if not online_mode or game_state == "GAMEPLAY" else network_players
                npc_collision_radius = 24  

                player_moved = False

                can_move_x = False
                if 0 <= int(cx_plus / TILE_SIZE) < map_size_x:
                    if active_map[int(player_y / TILE_SIZE)][int(cx_plus / TILE_SIZE)] == 0:
                        can_move_x = True

                if can_move_x:
                    for npc in targets:
                        if npc.alive:
                            if math.hypot(new_x - npc.x, player_y - npc.y) < npc_collision_radius:
                                can_move_x = False
                                break

                if can_move_x:
                    player_x = new_x
                    player_moved = True

                can_move_y = False
                if 0 <= int(cy_plus / TILE_SIZE) < map_size_y:
                    if active_map[int(cy_plus / TILE_SIZE)][int(player_x / TILE_SIZE)] == 0:
                        can_move_y = True

                if can_move_y:
                    for npc in targets:
                        if npc.alive:
                            if math.hypot(player_x - npc.x, new_y - npc.y) < npc_collision_radius:
                                can_move_y = False
                                break

                if can_move_y:
                    player_y = new_y
                    player_moved = True

                if player_moved:
                    send_my_position()

            if game_state == "GAMEPLAY" and not has_gun and player_alive:
                if math.hypot(player_x - gun_world_x, player_y - gun_world_y) < 30 and keys[pygame.K_e]:
                    has_gun = True

            if game_state == "GAMEPLAY" and len(active_npcs) > 0 and not any(n.alive for n in active_npcs):
                game_state = "LOBBY"
                has_gun = True 

            if is_shooting:
                shoot_frame += 1
                if shoot_frame <= 3: recoil_offset_y = (shoot_frame * 12)
                elif shoot_frame <= 12: recoil_offset_y = 36 - ((shoot_frame - 3) * 4)
                else:
                    is_shooting = False
                    recoil_offset_y = 0

            if muzzle_flash_timer > 0: muzzle_flash_timer -= 1
            for n in active_npcs + network_players:
                if n.flash_timer > 0: n.flash_timer -= 1

        # --- DRAW DISPATCHER ---
        try:
            screen.fill(BLACK)

            if game_state in ["GAMEPLAY", "NEIGHBORHOOD"]:
                horizon_shift = int(player_z * 2)
                center_horizon_y = HEIGHT // 2 + horizon_shift

                # Ceilings / Skies
                if map_name == "TECH ROOM":
                    pygame.draw.rect(screen, DARK_CORE, (0, 0, WIDTH, center_horizon_y))  
                    for y in range(0, HEIGHT // 2, 25):
                        render_y = y + horizon_shift
                        intensity = int(180 * (y / (HEIGHT // 2)))
                        color_ceil = (0, int(ROOF_BEAM[1] * (intensity / 255)), int(ROOF_BEAM[2] * (intensity / 255)))
                        pygame.draw.line(screen, color_ceil, (0, render_y), (WIDTH, render_y), 1)
                    for x in range(0, WIDTH, 100):
                        pygame.draw.line(screen, ROOF_BEAM, (x, horizon_shift), (WIDTH // 2, center_horizon_y), 1)
                else:
                    # Panoramic Skybox linked to the player's rotatable view angle
                    sky_width_factor = 2400
                    sky_offset = int((player_angle % (2 * math.pi)) * (sky_width_factor / (2 * math.pi)))

                    # Render a procedural ultra-smooth skybox gradient surface stretching with rotation
                    for y in range(0, center_horizon_y, 4):
                        t = y / max(1, center_horizon_y)
                        r_sky = int(SKY_BLUE[0] * (1 - t) + SKY_HORIZON[0] * t)
                        g_sky = int(SKY_BLUE[1] * (1 - t) + SKY_HORIZON[1] * t)
                        b_sky = int(SKY_BLUE[2] * (1 - t) + SKY_HORIZON[2] * t)
                        pygame.draw.rect(screen, (r_sky, g_sky, b_sky), (0, y, WIDTH, 4))

                    # Render atmospheric physical clouds that drift behind buildings realistically
                    pygame.draw.ellipse(screen, (245, 248, 255), (int((WIDTH // 2 - sky_offset) % sky_width_factor) - 400, 60 + horizon_shift, 260, 50))
                    pygame.draw.ellipse(screen, (235, 242, 255), (int((WIDTH // 2 - sky_offset + 800) % sky_width_factor) - 400, 30 + horizon_shift, 380, 70))
                    pygame.draw.ellipse(screen, (250, 252, 255), (int((WIDTH // 2 - sky_offset + 1600) % sky_width_factor) - 400, 80 + horizon_shift, 200, 40))

                # Floors / Terrains
                if map_name == "TECH ROOM":
                    pygame.draw.rect(screen, BLACK, (0, center_horizon_y, WIDTH, HEIGHT - center_horizon_y))
                    for y in range(HEIGHT // 2, HEIGHT, 20):
                        render_y = y + horizon_shift
                        intensity = int(255 * ((HEIGHT - y) / (HEIGHT // 2)))
                        color_floor = (0, int(FLOOR_GRID[1] * (intensity / 255)), int(FLOOR_GRID[2] * (intensity / 255)))
                        pygame.draw.line(screen, color_floor, (0, render_y), (WIDTH, render_y), 1)
                    for x in range(-200, WIDTH + 200, 80):
                        pygame.draw.line(screen, FLOOR_GRID, (WIDTH // 2, center_horizon_y), (x + int(math.sin(tick_counter * 0.01) * 10), HEIGHT + horizon_shift), 1)
                else:
                    # Floor perspective scanning
                    base_grass = SOCCER_PITCH_GREEN if map_name == "SOCCER STADIUM" else GRASS_GREEN
                    pygame.draw.rect(screen, base_grass, (0, center_horizon_y, WIDTH, HEIGHT - center_horizon_y))

                    for y in range(center_horizon_y, HEIGHT, 2):
                        norm_depth = (y - center_horizon_y) / max(1, HEIGHT - center_horizon_y)
                        # Clean Exponential Lighting Drop-off for beautiful distance fading
                        shading = (norm_depth ** 2) * 0.85 + 0.15
                        grain_density = max(1, int(12 * norm_depth))

                        g_r = int(base_grass[0] * shading)
                        g_g = int(base_grass[1] * shading)
                        g_b = int(base_grass[2] * shading)

                        pygame.draw.rect(screen, (g_r, g_g, g_b), (0, y, WIDTH, 2))

                        if norm_depth > 0.1:
                            num_blades = int(25 * norm_depth)
                            for _ in range(num_blades):
                                bx = random.randint(0, WIDTH)
                                color_shift = random.choice([-15, -5, 10, 20])
                                b_r = max(0, min(255, g_r + color_shift))
                                b_g = max(0, min(255, g_g + color_shift + (8 if color_shift > 0 else 0)))
                                b_b = max(0, min(255, g_b + color_shift // 2))

                                pygame.draw.rect(screen, (b_r, b_g, b_b), (bx, y - random.randint(0, grain_density), max(1, grain_density // 2), max(1, grain_density)))

                    if map_name == "SOCCER STADIUM":
                        for y in range(center_horizon_y, HEIGHT, 40):
                            norm_depth = (y - center_horizon_y) / max(1, HEIGHT - center_horizon_y)
                            alpha_fade = int(255 * norm_depth)
                            pygame.draw.line(screen, (alpha_fade, alpha_fade, alpha_fade), (0, y), (WIDTH, y), max(1, int(4 * norm_depth)))
                    else:
                        pygame.draw.polygon(screen, ASPHALT_ROAD, [(WIDTH//2 - 60, center_horizon_y), (WIDTH//2 + 60, center_horizon_y), (WIDTH + 300, HEIGHT), (-300, HEIGHT)])
                        pygame.draw.line(screen, WHITE, (WIDTH//2, center_horizon_y), (WIDTH//2, HEIGHT), 2)

                wall_depths = [float(MAX_DEPTH)] * max_rays_render

                start_angle = player_angle - HALF_FOV
                for ray in range(max_rays_render):
                    for depth in range(1, MAX_DEPTH, 1):  
                        target_x = player_x + depth * math.cos(start_angle)
                        target_y = player_y + depth * math.sin(start_angle)
                        col = int(target_x / TILE_SIZE)
                        row = int(target_y / TILE_SIZE)

                        if 0 <= col < map_size_x and 0 <= row < map_size_y:
                            wall_type = active_map[row][col]
                            if wall_type > 0:
                                corrected_depth = depth * math.cos(player_angle - start_angle)
                                wall_depths[ray] = corrected_depth  

                                wall_height = min(int((TILE_SIZE * 420) / (corrected_depth + 0.0001)), HEIGHT)
                                rect_y = center_horizon_y - (wall_height // 2)

                                hit_x = target_x % TILE_SIZE
                                hit_y = target_y % TILE_SIZE

                                dist_x = min(hit_x, TILE_SIZE - hit_x)
                                dist_y = min(hit_y, TILE_SIZE - hit_y)
                                if dist_x < dist_y:
                                    is_y_face = True
                                    hit_frac = hit_y / TILE_SIZE
                                else:
                                    is_y_face = False
                                    hit_frac = hit_x / TILE_SIZE

                                # Texture-Mapping & Slicing engine instead of plain solid rectangles
                                if wall_type in TEXTURES:
                                    tex = TEXTURES[wall_type]
                                    tex_x = int(hit_frac * (TEX_SIZE - 1))
                                    tex_x = max(0, min(TEX_SIZE - 1, tex_x))

                                    # Extract a 1px vertical column from our procedural image matching ray hit position
                                    tex_slice = pygame.Surface((1, TEX_SIZE))
                                    tex_slice.blit(tex, (0, 0), (tex_x, 0, 1, TEX_SIZE))

                                    # Scale the 1-pixel strip precisely to match perspective 3D projection height
                                    scaled_slice = pygame.transform.scale(tex_slice, (int(SCALE), int(wall_height)))

                                    # --- LIGHTING & DEPTH FOG FADING EFFECTS ---
                                    # UPGRADE: Dynamic Cross-Face Shading (Simulates physical overhead sun angle variance)
                                    shadow_factor = 0.65 if is_y_face else 0.92

                                    # Atmospheric Depth Fog Shading (gracefully dissolves assets into distant horizon)
                                    distance_fog = 1.0 / (1.0 + corrected_depth * corrected_depth * 0.00002)
                                    final_lighting = shadow_factor * distance_fog

                                    # Apply values directly onto the slice surface using a lighting layer mask
                                    shade_mask = pygame.Surface(scaled_slice.get_size())
                                    shade_mask.fill((int(255 * final_lighting), int(255 * final_lighting), int(255 * final_lighting)))
                                    scaled_slice.blit(shade_mask, (0, 0), special_flags=pygame.BLEND_MULT)

                                    # Write sliced structural elements down onto the output frame
                                    screen.blit(scaled_slice, (int(ray * SCALE), int(rect_y)))
                                else:
                                    # Fallback color matrix renderer for basic types
                                    if wall_type == 1: base_color = TECH_CYAN
                                    elif wall_type == 2: base_color = MATRIX_GREEN
                                    else: base_color = HOUSE_BROWN

                                    shadow = 255 / (1 + corrected_depth * corrected_depth * 0.00004)
                                    side_lighting_multiplier = 0.75 if is_y_face else 1.0
                                    final_shadow = (shadow / 255.0) * side_lighting_multiplier
                                    r_col = int(base_color[0] * final_shadow)
                                    g_col = int(base_color[1] * final_shadow)
                                    b_col = int(base_color[2] * final_shadow)
                                    pygame.draw.rect(screen, (r_col, g_col, b_col), (int(ray * SCALE), int(rect_y), int(SCALE), int(wall_height)))

                                # Extra Architectural Overlays (Roofs, and trim elements layered on top)
                                if game_state == "NEIGHBORHOOD":
                                    shadow = 255 / (1 + corrected_depth * corrected_depth * 0.00004)
                                    side_lighting_multiplier = 0.75 if is_y_face else 1.0
                                    final_shadow = (shadow / 255.0) * side_lighting_multiplier

                                    if wall_type in [3, 4, 5]: 
                                        roof_slope_offset = int((wall_height // 3) * (0.5 - abs(hit_frac - 0.5)))
                                        roof_height = (wall_height // 2) - roof_slope_offset
                                        roof_y_top = rect_y - roof_height
                                        roof_base_color = (50, 55, 62)
                                        roof_shaded = (int(roof_base_color[0] * final_shadow), int(roof_base_color[1] * final_shadow), int(roof_base_color[2] * final_shadow))
                                        pygame.draw.rect(screen, roof_shaded, (int(ray * SCALE), int(roof_y_top), int(SCALE), int(roof_height)))
                                        if int(roof_y_top * 0.1) % 2 == 0:
                                            pygame.draw.rect(screen, (max(0, roof_shaded[0]-15), max(0, roof_shaded[1]-15), max(0, roof_shaded[2]-15)), (int(ray * SCALE), int(roof_y_top), int(SCALE), max(1, roof_height // 8)))
                                        eave_color = (int(220 * final_shadow), int(220 * final_shadow), int(220 * final_shadow))
                                        pygame.draw.rect(screen, eave_color, (int(ray * SCALE), int(rect_y), int(SCALE), max(1, int(wall_height // 40))))

                                    # Architectural Window Panes
                                    if wall_type in [3, 4, 6] and ((0.16 < hit_frac < 0.36) or (0.64 < hit_frac < 0.84)):
                                        win_y_top = rect_y + wall_height // 4
                                        win_height = wall_height // 3
                                        win_color = (int(WINDOW_BLUE[0] * final_shadow), int(WINDOW_BLUE[1] * final_shadow), int(WINDOW_BLUE[2] * final_shadow))
                                        pygame.draw.rect(screen, win_color, (int(ray * SCALE), int(win_y_top), int(SCALE), int(win_height)))

                                        # UPGRADE: Realistic Glass Specular Reflection Angle Highlight
                                        if (0.22 < hit_frac < 0.28) or (0.70 < hit_frac < 0.76):
                                            glare_color = (int(200 * final_shadow), int(230 * final_shadow), int(255 * final_shadow))
                                            pygame.draw.rect(screen, glare_color, (int(ray * SCALE), int(win_y_top), int(SCALE), int(win_height // 2)))

                                        trim_color = (int(240 * final_shadow), int(240 * final_shadow), int(240 * final_shadow))
                                        pygame.draw.rect(screen, trim_color, (int(ray * SCALE), int(win_y_top), int(SCALE), max(2, int(wall_height // 40))))
                                        if (win_y_top + win_height) < HEIGHT:
                                            pygame.draw.rect(screen, trim_color, (int(ray * SCALE), int(win_y_top + win_height - 2), int(SCALE), max(2, int(wall_height // 40))))
                                        pygame.draw.rect(screen, trim_color, (int(ray * SCALE), int(win_y_top + (win_height // 2)), int(SCALE), max(1, int(wall_height // 60))))
                                        if (0.25 < hit_frac < 0.27) or (0.73 < hit_frac < 0.75):
                                            pygame.draw.rect(screen, trim_color, (int(ray * SCALE), int(win_y_top), int(SCALE), int(win_height)))
                                break
                    start_angle += DELTA_ANGLE

                # Render Gun Pickup Crate
                if game_state == "GAMEPLAY" and not has_gun:
                    vec_x, vec_y = gun_world_x - player_x, gun_world_y - player_y
                    dist_to_gun = math.hypot(vec_x, vec_y)
                    gun_angle = math.atan2(vec_y, vec_x) - player_angle
                    while gun_angle > math.pi: gun_angle -= 2 * math.pi
                    while gun_angle < -math.pi: gun_angle += 2 * math.pi
                    if -HALF_FOV < gun_angle < HALF_FOV and dist_to_gun > 0:
                        screen_x = int((WIDTH // 2) + (gun_angle / (FOV / WIDTH)))
                        gun_size = min(int((TILE_SIZE * 300) / dist_to_gun), 300)
                        screen_y = center_horizon_y - (gun_size // 4)
                        pygame.draw.rect(screen, GUN_STEEL, (int(screen_x - gun_size // 2), int(screen_y), int(gun_size), int(gun_size // 2)))
                        pygame.draw.rect(screen, TECH_CYAN, (int(screen_x - gun_size // 2), int(screen_y), int(gun_size), int(gun_size // 2)), 2)
                        if dist_to_gun < 30:
                            prompt_text = font.render("[PRESS 'E' TO GRAB WEAPON]", True, MATRIX_GREEN)
                            screen.blit(prompt_text, (WIDTH // 2 - 170, HEIGHT - 150))

                # Actor Rendering Engine
                current_actors = active_npcs if not online_mode or game_state == "GAMEPLAY" else network_players
                for actor in current_actors:
                    if not actor.alive: continue
                    npc_vec_x, npc_vec_y = actor.x - player_x, actor.y - player_y
                    npc_dist = math.hypot(npc_vec_x, npc_vec_y)
                    npc_ang = math.atan2(npc_vec_y, npc_vec_x) - player_angle
                    while npc_ang > math.pi: npc_ang -= 2 * math.pi
                    while npc_ang < -math.pi: npc_ang += 2 * math.pi

                    if -HALF_FOV < npc_ang < HALF_FOV and npc_dist > 10:
                        proj_dist = npc_dist * math.cos(npc_ang)
                        npc_ray = int((npc_ang + HALF_FOV) / DELTA_ANGLE)
                        if 0 <= npc_ray < max_rays_render and proj_dist < wall_depths[npc_ray]:
                            h = min(int((TILE_SIZE * 480) / proj_dist), 520)
                            w = h // 2
                            light_mod = min(1.0, 300 / (proj_dist + 0.001))

                            def apply_lighting(rgb, flash=False):
                                if actor.flash_timer > 0: return (240, 50, 50) if not flash else (255, 160, 160)
                                return (int(rgb[0] * light_mod), int(rgb[1] * light_mod), int(rgb[2] * light_mod))

                            suit_rgb = (180, 70, 20) if (online_mode and game_state == "NEIGHBORHOOD") else (45, 55, 75)
                            c_suit = apply_lighting(suit_rgb)
                            c_suit_dark = apply_lighting((30, 32, 40))
                            c_armor = apply_lighting((20, 24, 30))
                            c_skin = apply_lighting(SKIN_BASE, True)
                            c_skin_shadow = apply_lighting(SKIN_SHADOW)
                            c_visor = apply_lighting((0, 190, 255)) if actor.flash_timer == 0 else (255, 255, 255)

                            x = int(npc_ray * SCALE) + (random.randint(-4, 4) if actor.flash_timer > 0 else 0)

                            # Legs
                            leg_w = max(2, w // 5)
                            leg_h = h // 3
                            pelvis_y = center_horizon_y + h // 10
                            pygame.draw.rect(screen, c_suit_dark, (int(x - w // 4), int(pelvis_y), int(leg_w), int(leg_h)))
                            pygame.draw.rect(screen, c_suit_dark, (int(x + w // 4 - leg_w), int(pelvis_y), int(leg_w), int(leg_h)))
                            boot_h = max(3, h // 20)
                            pygame.draw.rect(screen, c_armor, (int(x - w // 4 - 2), int(pelvis_y + leg_h - boot_h), int(leg_w + 3), int(boot_h)))
                            pygame.draw.rect(screen, c_armor, (int(x + w // 4 - leg_w - 1), int(pelvis_y + leg_h - boot_h), int(leg_w + 3), int(boot_h)))

                            # Torso
                            torso_w = w // 2
                            torso_h = h // 3
                            torso_y = center_horizon_y - torso_h // 2
                            torso_poly = [(int(x - torso_w // 2), int(torso_y)), (int(x + torso_w // 2), int(torso_y)), 
                                          (int(x + torso_w // 3), int(torso_y + torso_h)), (int(x - torso_w // 3), int(torso_y + torso_h))]
                            pygame.draw.polygon(screen, c_suit, torso_poly)
                            armor_w = torso_w - max(4, w // 10)
                            armor_h = torso_h // 2
                            pygame.draw.rect(screen, c_armor, (int(x - armor_w // 2), int(torso_y + max(2, h // 40)), int(armor_w), int(armor_h)), 0, 4)

                            # Arms
                            arm_w = max(2, w // 7)
                            arm_h = torso_h - max(2, h // 30)
                            pygame.draw.line(screen, c_suit_dark, (int(x - torso_w // 2), int(torso_y + 4)), (int(x - torso_w // 2 - arm_w // 2), int(torso_y + arm_h)), int(arm_w))
                            pygame.draw.circle(screen, c_armor, (int(x - torso_w // 2), int(torso_y + 4)), int(arm_w))
                            pygame.draw.line(screen, c_suit_dark, (int(x + torso_w // 2), int(torso_y + 4)), (int(x + torso_w // 2 + arm_w // 2), int(torso_y + arm_h)), int(arm_w))
                            pygame.draw.circle(screen, c_armor, (int(x + torso_w // 2), int(torso_y + 4)), int(arm_w))

                            # Head
                            neck_w = max(2, w // 10)
                            neck_h = max(2, h // 35)
                            pygame.draw.rect(screen, c_skin_shadow, (int(x - neck_w // 2), int(torso_y - neck_h), int(neck_w), int(neck_h)))
                            head_w = max(6, w // 4)
                            head_h = max(8, h // 5)
                            head_y = torso_y - neck_h - head_h
                            pygame.draw.ellipse(screen, c_skin, (int(x - head_w // 2), int(head_y), int(head_w), int(head_h)))
                            visor_h = max(1, head_h // 6)
                            pygame.draw.rect(screen, c_visor, (int(x - head_w // 3), int(head_y + head_h // 4), int((head_w // 3) * 2), int(visor_h)))

                            # Enemy HP Bar
                            bar_w = w // 2
                            bar_h = max(4, h // 35)
                            pygame.draw.rect(screen, (30, 10, 10), (int(x - bar_w // 2), int(head_y - 15), int(bar_w), int(bar_h)))
                            pygame.draw.rect(screen, (255, 30, 70), (int(x - bar_w // 2), int(head_y - 15), int(bar_w * max(0, actor.hp / actor.max_hp)), int(bar_h)))
                            pygame.draw.rect(screen, WHITE, (int(x - bar_w // 2), int(head_y - 15), int(bar_w), int(bar_h)), 1)

                # Laser Beam Traces
                for beam in laser_beams[:]:
                    beam['age'] += 1
                    pct = beam['age'] / beam['max_age']
                    laser_w = int(25 * (1.0 - pct))
                    laser_y_start = int(center_horizon_y + 60 + (recoil_offset_y))
                    current_y = laser_y_start - int((laser_y_start - center_horizon_y) * pct)
                    if current_y > center_horizon_y and laser_w > 0:
                        pygame.draw.line(screen, (255, 255, 255), (WIDTH // 2, laser_y_start), (WIDTH // 2, current_y), laser_w)
                        pygame.draw.line(screen, TECH_CYAN, (WIDTH // 2, laser_y_start), (WIDTH // 2, current_y), max(1, laser_w // 2))
                    else:
                        laser_beams.remove(beam)

                # First Person Arms/Hands bobbing
                is_moving = any(keys[k] for k in [pygame.K_UP, pygame.K_DOWN, pygame.K_LEFT, pygame.K_RIGHT, pygame.K_w, pygame.K_s, pygame.K_a, pygame.K_d])
                bob_x = int(math.cos(tick_counter * 0.15) * 5) if is_moving else 0
                current_bob_y = (int(math.sin(tick_counter * 0.15) * 4) if is_moving else int(math.sin(tick_counter * 0.05) * 1.5)) + recoil_offset_y + int(player_z * 0.5)

                if not has_gun:
                    # Left Hand
                    lh_x = WIDTH // 4 - 50 + bob_x
                    lh_y = HEIGHT - 200 + current_bob_y
                    pygame.draw.polygon(screen, SKIN_DARK_SHADOW, [(lh_x - 30, HEIGHT), (lh_x + 40, HEIGHT), (lh_x + 35, lh_y + 15), (lh_x - 10, lh_y + 25)])
                    pygame.draw.polygon(screen, SKIN_SHADOW, [(lh_x - 25, HEIGHT), (lh_x + 35, HEIGHT), (lh_x + 20, lh_y + 80), (lh_x - 10, lh_y + 85)])
                    pygame.draw.polygon(screen, SKIN_BASE, [(lh_x - 18, HEIGHT), (lh_x + 28, HEIGHT), (lh_x + 15, lh_y + 82), (lh_x - 5, lh_y + 85)])
                    pygame.draw.rect(screen, SLEEVE_COLOR, (lh_x - 30, lh_y + 105, 75, 120))
                    pygame.draw.polygon(screen, SKIN_SHADOW, [(lh_x - 10, lh_y + 85), (lh_x + 20, lh_y + 80), (lh_x + 32, lh_y + 25), (lh_x + 15, lh_y + 20), (lh_x - 3, lh_y + 45)])
                    pygame.draw.polygon(screen, SKIN_BASE, [(lh_x - 6, lh_y + 83), (lh_x + 16, lh_y + 79), (lh_x + 28, lh_y + 27), (lh_x + 14, lh_y + 23), (lh_x - 1, lh_y + 46)])
                    draw_tapered_finger(screen, lh_x + 20, lh_y + 58, 38, -5, 6, SKIN_BASE, SKIN_SHADOW)
                    draw_tapered_finger(screen, lh_x + 24, lh_y + 46, 44, -2, 7, SKIN_BASE, SKIN_SHADOW)
                    draw_tapered_finger(screen, lh_x + 26, lh_y + 34, 48, 1, 7, SKIN_BASE, SKIN_SHADOW)
                    draw_tapered_finger(screen, lh_x + 28, lh_y + 22, 50, 4, 8, SKIN_HIGH, SKIN_SHADOW)
                    draw_tapered_finger(screen, lh_x + 12, lh_y + 36, 32, 38, 7, SKIN_HIGH, SKIN_SHADOW)

                    # Right Hand
                    rh_x = (WIDTH // 4) * 3 + 20 + bob_x
                    rh_y = HEIGHT - 200 + current_bob_y
                    pygame.draw.polygon(screen, SKIN_DARK_SHADOW, [(rh_x - 40, HEIGHT), (rh_x + 30, HEIGHT), (rh_x + 10, rh_y + 25), (rh_x - 35, rh_y + 15)])
                    pygame.draw.polygon(screen, SKIN_SHADOW, [(rh_x - 35, HEIGHT), (rh_x + 25, HEIGHT), (rh_x + 10, rh_y + 85), (rh_x - 20, rh_y + 80)])
                    pygame.draw.polygon(screen, SKIN_BASE, [(rh_x - 28, HEIGHT), (rh_x + 18, HEIGHT), (rh_x + 5, rh_y + 85), (rh_x - 15, rh_y + 82)])
                    pygame.draw.rect(screen, SLEEVE_COLOR, (rh_x - 45, rh_y + 105, 75, 120))
                    pygame.draw.polygon(screen, SKIN_SHADOW, [(rh_x - 20, rh_y + 80), (rh_x + 10, rh_y + 85), (rh_x + 3, rh_y + 45), (rh_x - 15, rh_y + 20), (rh_x - 32, rh_y + 25)])
                    pygame.draw.polygon(screen, SKIN_BASE, [(rh_x - 16, rh_y + 79), (rh_x +  6, rh_y + 83), (rh_x + 1, rh_y + 46), (rh_x - 14, rh_y + 23), (rh_x - 28, rh_y + 27)])
                    draw_tapered_finger(screen, rh_x - 20, rh_y + 58, 38, -5, 6, SKIN_BASE, SKIN_SHADOW, mirror=True)
                    draw_tapered_finger(screen, rh_x - 24, rh_y + 46, 44, -2, 7, SKIN_BASE, SKIN_SHADOW, mirror=True)
                    draw_tapered_finger(screen, rh_x - 26, rh_y + 34, 48, 1, 7, SKIN_BASE, SKIN_SHADOW, mirror=True)
                    draw_tapered_finger(screen, rh_x - 28, rh_y + 22, 50, 4, 8, SKIN_HIGH, SKIN_SHADOW, mirror=True)
                    draw_tapered_finger(screen, rh_x - 12, rh_y + 36, 32, 38, 7, SKIN_HIGH, SKIN_SHADOW, mirror=True)
                else:
                    center_x = WIDTH // 2 + bob_x
                    center_y = center_horizon_y + 100 + current_bob_y
                    pygame.draw.polygon(screen, GUN_DARK, [(center_x - 30, center_y), (center_x + 30, center_y), (center_x + 55, HEIGHT), (center_x - 55, HEIGHT)])
                    pygame.draw.polygon(screen, GUN_STEEL, [(center_x - 20, center_y), (center_x + 20, center_y), (center_x + 35, HEIGHT), (center_x - 35, HEIGHT)])
                    pygame.draw.polygon(screen, GUN_METAL, [(center_x - 12, center_y + 15), (center_x + 12, center_y + 15), (center_x + 20, HEIGHT), (center_x - 20, HEIGHT)])
                    pygame.draw.rect(screen, GUN_DARK, (center_x - 22, center_y + 2, 12, 12)) 
                    pygame.draw.rect(screen, GUN_DARK, (center_x + 10, center_y + 2, 12, 12)) 
                    pygame.draw.rect(screen, MATRIX_GREEN, (center_x - 2, center_y - 6, 4, 10))
                    pygame.draw.polygon(screen, (15, 18, 22), [(center_x - 25, center_y + 40), (center_x + 25, center_y + 40), (center_x + 45, HEIGHT), (center_x - 45, HEIGHT)])
                    pulse = int(180 + math.sin(tick_counter * 0.2) * 55)
                    pygame.draw.line(screen, (0, pulse, 255), (center_x - 28, center_y + 60), (center_x - 40, HEIGHT), 3)
                    pygame.draw.line(screen, (0, pulse, 255), (center_x + 28, center_y + 60), (center_x + 40, HEIGHT), 3)

                    pygame.draw.rect(screen, SLEEVE_COLOR, (center_x - 120, center_y + 100, 60, 110))
                    pygame.draw.ellipse(screen, SKIN_SHADOW, (center_x - 75, center_y + 75, 42, 45))
                    pygame.draw.ellipse(screen, SKIN_BASE, (center_x - 72, center_y + 75, 40, 41))
                    pygame.draw.ellipse(screen, SKIN_HIGH, (center_x - 45, center_y + 82, 22, 11)) 
                    pygame.draw.ellipse(screen, SKIN_NAIL, (center_x - 28, center_y + 84, 6, 6))

                    pygame.draw.rect(screen, SLEEVE_COLOR, (center_x + 60, center_y + 100, 60, 110))
                    pygame.draw.ellipse(screen, SKIN_SHADOW, (center_x + 33, center_y + 75, 42, 45))
                    pygame.draw.ellipse(screen, SKIN_BASE, (center_x + 32, center_y + 75, 40, 41))
                    pygame.draw.ellipse(screen, SKIN_HIGH, (center_x + 23, center_y + 82, 22, 11))
                    pygame.draw.ellipse(screen, SKIN_NAIL, (center_x + 22, center_y + 84, 6, 6))

                    if muzzle_flash_timer > 0:
                        flash_radius = random.randint(35, 55)
                        pygame.draw.circle(screen, WHITE, (center_x, center_y), flash_radius // 2)
                        pygame.draw.circle(screen, TECH_CYAN, (center_x, center_y), flash_radius, 3)

                crosshair_x = WIDTH // 2
                crosshair_y = HEIGHT // 2
                pygame.draw.line(screen, (255, 255, 255), (crosshair_x - CROSSHAIR_SIZE, crosshair_y), (crosshair_x - 2, crosshair_y), 2)
                pygame.draw.line(screen, (255, 255, 255), (crosshair_x + 2, crosshair_y), (crosshair_x + CROSSHAIR_SIZE, crosshair_y), 2)
                pygame.draw.line(screen, (255, 255, 255), (crosshair_x, crosshair_y - CROSSHAIR_SIZE), (crosshair_x, crosshair_y - 2), 2)
                pygame.draw.line(screen, (255, 255, 255), (crosshair_x, crosshair_y + 2), (crosshair_x, crosshair_y + CROSSHAIR_SIZE), 2)
                pygame.draw.circle(screen, TECH_CYAN if game_state == "GAMEPLAY" else WHITE, (crosshair_x, crosshair_y), 6, 1)

                # --- OPTICAL ENGINE: VIGNETTE PASS ---
                # Blits the physical vignetting texture mask on top of the environment layout
                screen.blit(VIGNETTE_MASK, (0, 0))

                # --- OPTICAL ENGINE: FILM GRAIN SHADER PASS ---
                # Creates tiny variations of structural pixel noise to make layouts look organic
                for _ in range(40 if IS_BROWSER else 120):
                    gx = random.randint(0, WIDTH - 1)
                    gy = random.randint(0, HEIGHT - 1)
                    grain_surf = pygame.Surface((2, 2), pygame.SRCALPHA)
                    grain_surf.fill((255, 255, 255, random.randint(10, 30)))
                    screen.blit(grain_surf, (gx, gy))

                # Mini Map Display
                radar_x, radar_y = 20, 20
                radar_scale = 12
                pygame.draw.rect(screen, (10, 15, 20) if game_state == "GAMEPLAY" else (30, 40, 35), (radar_x, radar_y, map_size_x * radar_scale, map_size_y * radar_scale))
                pygame.draw.rect(screen, TECH_CYAN if game_state == "GAMEPLAY" else GRASS_GREEN, (radar_x, radar_y, map_size_x * radar_scale, map_size_y * radar_scale), 1)

                for r in range(map_size_y):
                    for c in range(map_size_x):
                        if active_map[r][c] > 0:
                            if game_state == "GAMEPLAY":
                                map_color = ROOF_BEAM
                            else:
                                if active_map[r][c] == 4: map_color = HOUSE_BROWN
                                elif active_map[r][c] == 3: map_color = BRICK_RED
                                elif active_map[r][c] == 6: map_color = STADIUM_WHITE
                                elif active_map[r][c] == 7: map_color = GOAL_YELLOW
                                else: map_color = (130, 100, 80)
                            pygame.draw.rect(screen, map_color, (radar_x + c * radar_scale, radar_y + r * radar_scale, radar_scale - 1, radar_scale - 1))

                p_map_x = int((player_x / TILE_SIZE) * radar_scale) + radar_x
                p_map_y = int((player_y / TILE_SIZE) * radar_scale) + radar_y
                pygame.draw.circle(screen, MATRIX_GREEN if game_state == "GAMEPLAY" else (240, 240, 50), (p_map_x, p_map_y), 3)

                # RENDER OPPONENT ON MINIMAP IF ONLINE
                if online_mode and network_players and len(network_players) > 0:
                    opp = network_players[0]
                    opp_map_x = int((opp.x / TILE_SIZE) * radar_scale) + radar_x
                    opp_map_y = int((opp.y / TILE_SIZE) * radar_scale) + radar_y
                    if radar_x <= opp_map_x <= radar_x + (map_size_x * radar_scale) and radar_y <= opp_map_y <= radar_y + (map_size_y * radar_scale):
                        pygame.draw.circle(screen, (255, 50, 50), (opp_map_x, opp_map_y), 3)

                lbl_text = f"MAP: {map_name}"
                lbl = mini_font.render(lbl_text, True, MATRIX_GREEN if game_state == "GAMEPLAY" else WHITE)
                screen.blit(lbl, (radar_x, radar_y + (map_size_y * radar_scale) + 4))

                # HUD player health indicators
                hud_bar_w = 200
                hud_bar_h = 20
                hud_x = WIDTH - hud_bar_w - 20
                hud_y = HEIGHT - hud_bar_h - 20
                pygame.draw.rect(screen, (30, 10, 10), (hud_x, hud_y, hud_bar_w, hud_bar_h))
                pygame.draw.rect(screen, (50, 255, 100) if player_hp > 30 else (255, 30, 30), 
                                 (hud_x, hud_y, int(hud_bar_w * (player_hp / player_max_hp)), hud_bar_h))
                pygame.draw.rect(screen, WHITE, (hud_x, hud_y, hud_bar_w, hud_bar_h), 2)
                hp_lbl = mini_font.render(f"HP: {player_hp}/{player_max_hp}", True, WHITE)
                screen.blit(hp_lbl, (hud_x, hud_y - 16))

                if not player_alive:
                    death_overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
                    death_overlay.fill((150, 0, 0, 100)) 
                    screen.blit(death_overlay, (0, 0))
                    game_over_text = large_font.render("TERMINATED", True, WHITE)
                    respawn_text = mini_font.render("Press ESC to return to Menu", True, WHITE)
                    screen.blit(game_over_text, (WIDTH // 2 - game_over_text.get_width() // 2, HEIGHT // 2 - 20))
                    screen.blit(respawn_text, (WIDTH // 2 - respawn_text.get_width() // 2, HEIGHT // 2 + 30))
                    if keys[pygame.K_ESCAPE]:
                        game_state = "MENU"

            elif game_state == "LOBBY":
                screen.fill(DARK_CORE)
                pygame.draw.rect(screen, TECH_CYAN, (40, 40, WIDTH - 80, HEIGHT - 80), 3, 8)
                pygame.draw.line(screen, TECH_CYAN, (40, 110), (WIDTH - 40, 110), 2)

                title = large_font.render("TERMINAL ACCESS LOBBY", True, TECH_CYAN)
                screen.blit(title, (WIDTH // 2 - title.get_width() // 2, 60))

                if is_searching:
                    col_search = (255, 215, 0)
                    pygame.draw.rect(screen, col_search, btn_online_rect, 2, 4)
                    txt_search = font.render("searching for players...", True, col_search)
                    screen.blit(txt_search, (btn_online_rect.x + 30, btn_online_rect.y + 12))
                else:
                    col_on = MATRIX_GREEN if btn_online_rect.collidepoint(mouse_pos) else WHITE
                    pygame.draw.rect(screen, col_on, btn_online_rect, 2, 4)
                    txt_on = font.render("> JOIN ONLINE ROOM", True, col_on)
                    screen.blit(txt_on, (btn_online_rect.x + 40, btn_online_rect.y + 12))

                col_npc = MATRIX_GREEN if btn_npcs_rect.collidepoint(mouse_pos) else WHITE
                pygame.draw.rect(screen, col_npc, btn_npcs_rect, 2, 4)
                txt_npc = font.render("> JOIN ROOM WITH NPCS", True, col_npc)
                screen.blit(txt_npc, (btn_npcs_rect.x + 40, btn_npcs_rect.y + 12))

                footer_text = "SYSTEM STATUS: QUEUED..." if is_searching else "SYSTEM STATUS: STABLE // CONNECTION: READY"
                footer = mini_font.render(footer_text, True, ROOF_BEAM)
                screen.blit(footer, (60, HEIGHT - 75))

            elif game_state == "MAP_SELECT":
                screen.fill(DARK_CORE)
                pygame.draw.rect(screen, TECH_CYAN, (40, 40, WIDTH - 80, HEIGHT - 80), 3, 8)
                pygame.draw.line(screen, TECH_CYAN, (40, 110), (WIDTH - 40, 110), 2)

                title = large_font.render("SELECT FIELD TARGET", True, TECH_CYAN)
                screen.blit(title, (WIDTH // 2 - title.get_width() // 2, 60))

                col_map1 = MATRIX_GREEN if btn_map_neighborhood.collidepoint(mouse_pos) else WHITE
                pygame.draw.rect(screen, col_map1, btn_map_neighborhood, 2, 4)
                txt_map1 = font.render("[1] NEIGHBORHOOD DISTRICT", True, col_map1)
                screen.blit(txt_map1, (btn_map_neighborhood.x + 35, btn_map_neighborhood.y + 12))

                col_map2 = MATRIX_GREEN if btn_map_soccer.collidepoint(mouse_pos) else WHITE
                pygame.draw.rect(screen, col_map2, btn_map_soccer, 2, 4)
                txt_map2 = font.render("[2] SOCCER STADIUM FIELD", True, col_map2)
                screen.blit(txt_map2, (btn_map_soccer.x + 45, btn_map_soccer.y + 12))
                col_map3 = MATRIX_GREEN if btn_map_space.collidepoint(mouse_pos) else WHITE
                pygame.draw.rect(screen, col_map3, btn_map_space, 2, 4)
                txt_map3 = font.render("[3] DEEP SPACE STATION", True, col_map3)
                screen.blit(txt_map3, (btn_map_space.x + 35, btn_map_space.y + 10))

            elif game_state == "MENU":
                screen.fill((10, 12, 22))
                title_text = large_font.render("ELIMINATION CHANNELS", True, TECH_CYAN)
                instr_text = font.render("Eliminate the core NPC unit to breach terminal.", True, WHITE)
                screen.blit(title_text, (WIDTH // 2 - title_text.get_width() // 2, HEIGHT // 2 - 100))
                screen.blit(instr_text, (WIDTH // 2 - instr_text.get_width() // 2, HEIGHT // 2 - 30))
                btn_color = MATRIX_GREEN if start_btn_rect.collidepoint(mouse_pos) else TECH_CYAN
                pygame.draw.rect(screen, btn_color, start_btn_rect, 2)
                btn_text = font.render("START SYSTEM", True, btn_color)
                screen.blit(btn_text, (start_btn_rect.x + 18, start_btn_rect.y + 12))

            pygame.display.flip()
        except Exception as e:
            pass


        clock.tick(60)
        await asyncio.sleep(0)

    pygame.quit()



if __name__ == "__main__" or IS_BROWSER:
    asyncio.run(main())


# while True:
# while running:

import numpy as np
import pygame
from pygame.math import Vector2

N_PHASES_SHIP = 6
MOD_PHASE_SHIP = 4*(N_PHASES_SHIP-1)
WORLD_SIZE = (20,20)
WRECK_COORD = (WORLD_SIZE[0]//2, WORLD_SIZE[1]//2)
MAX_DIST = None
WORLD_SIZE_PIX = None
MAX_VILLAGE_DIST = 0.2

MUSIC = True

SHOW_GRID = False

CHAR_SIZE = 10
S = None
CENTER = None
FPS = 100
GIROUETTE_LENGTH = 40
GIROUETTE_COLOR = (50,50,50)
DT = 0.002

COLOR_SUCCESS = (0,255,0)
COLOR_FAIL = (255,100,0)
FAIL_FACTOR = 1.4
SUCCESS_FACTOR = 1.4


SUMMER_LEVEL = 0.6
WINTER_LEVEL = 0.52
WATER_LEVEL = SUMMER_LEVEL
SEASON_MOD_DAYS = 30

MIN_WINTER_TEMP = 2
TREASURE_PROB = 1.

I_FADING = FPS * 2
DAY_FACTOR = 1./500.

MAX_FLAGS = 3
READ_FLAG_DIST = 50

WIND_FACTOR = 0.2
WIND_FACTOR_SWIM = 0.08
DIR_FACTOR = 5.
FRICTION_FACTOR = 3.
COL_SIZE = 10
SWIMMING = 0.8
WALKING_SPEED = 0.5
SHIP_SPEED_FACTOR = 1.


KEY_DELAY = 1000//FPS
KEY_INTERVAL = 1000//FPS

DELTA_POS = 5 #for refresh last position
DELTA_SPACE_I = 20
BOARDING_DISTANCE = 50

LIFEBAR_SIZE = (100, 20)
COLLISION_FACTOR = 1./50

TEMP_IDEAL = 25
TEMP_0 = -40.
CLIMATE_FACTOR = (-TEMP_0 + 20)/0.5
#clim_temp * climate_factor ~ 0.5 * climate_factor ~ -parameters.TEMP_0 + 20
#==> climate_factor = (-parameters.TEMP_0 + 20)/0.5
TDX = 1. - SUMMER_LEVEL
TDY = -CLIMATE_FACTOR/2.
TGRAD = TDY / TDX
ALT_0 = -TGRAD*SUMMER_LEVEL
#height_temp = -climate_factor*0.5 for h = 1., height_temp = 0 for h = SUMMER_LEVEL
#h_temp = a*h + b.  a + b = -climate_factor/2 and a*SUMMER_LEVEL + b = 0
#==> b = -a*SUMMER_LEVEL and a -a*SUMMER_LEVEL = - climate_factor/2 = a*(1-water_level)
#==> a = -climate_factor/(2*(1-water_level))
TEMP_MAX = CLIMATE_FACTOR
THERMO_H_PIX = 42
TNORM_A = THERMO_H_PIX/(TEMP_MAX-TEMP_0)
TNORM_B = -TNORM_A*TEMP_0
#f(TEMP_0) = 0, f(TEMP_MAX) = 42 => f(T) = a*TEMP_0 + b = 0, a*TEMP_MAX + b = 42
#==> -a*TEMP_0 = 42 - a*TEMP_MAX ==> a*(TEMP_MAX-TEMP_0)=42


CRITICAL_FOOD = 50
FOOD_CANNIBAL = 200
FOOD_PER_TURN = 1
TBAD_FACTOR = 0.3
MAX_WSF = 200
MAX_VSF = 20
MOD_LIFE = 100

MAX_OSF = 20



MAX_CAMPS = 2
HUNT_FACTOR = 20.
_INIT_N_HUNT = 5 #must stay like this
MAX_HUNT_PROB = 0.9
MIN_HUNT_PROB = 0.1

FACTOR_ALT = 30000.

MOD_VILLAGE_FOOD_REGEN = 36000
VILLAGE_LEVEL = 1.2*SUMMER_LEVEL
VILLAGE_TRY = 20
VILLAGE_MAX_PROBABILITY = 1.
VILLAGE_MIN_PROBABILITY = 0.00001
MAX_VILLAGE_SIZE = 32
VILLAGE_SPACING = 1.2
HOUSE_SPACING = int(22*VILLAGE_SPACING)
HOUSE_RAND = 2*(HOUSE_SPACING - 20) #2*HOUSE_RAND < HOUSE_SPACING-house_img_size
MAX_VILLAGE_WIDTH = int(MAX_VILLAGE_SIZE**0.5)*HOUSE_SPACING + HOUSE_RAND

OASIS_PROB = 1.
FOREST_PROB = 1.

MOD_ELEMENTS = FPS

_COLLISION_POINTS = [(0,0),(COL_SIZE,0),(-COL_SIZE,0),(0,COL_SIZE),(0,-COL_SIZE)]
_NCOLL = len(_COLLISION_POINTS)

A_COLOR = (0,0,255)
H_COLOR = (0,255,0)
C_COLOR = (255,0,0)

BISURFACE = True
NCLOUDS = 0
CLOUD_ALPHA = 50
REFLECT = True
RAIN_IMPACTS = 10
RAIN_DISTRIBUTIONS = 50

USE_LOADER = True
RADIUS_LOAD = 5
RADIUS_FREE = 6
MAX_CHUNKS = int(3.14*RADIUS_FREE**2) + 1
MAX_MEMORY_USAGE = 1 #800

MOD_LOW = 10
MOD_SAVE_GAME = 500
FILE_SAVE = "save"

def set_world_size(size):
    global WORLD_SIZE, WORLD_SIZE_PIX, MAX_DIST, WRECK_COORD
    WORLD_SIZE = size
    WORLD_SIZE_PIX = Vector2(WORLD_SIZE)*S
    MAX_DIST = WORLD_SIZE_PIX/2
    WRECK_COORD = (WORLD_SIZE[0]//2, WORLD_SIZE[1]//2)


def get_memory_per_chunk():
    pygame_surface = S*S*4
    numpy_hmap = S*S*8
    return (pygame_surface + numpy_hmap)/1e6

def get_memory_all_chunks():
    return get_memory_per_chunk()*MAX_CHUNKS

def set_S(s):
    global S, _COLLISION_POINTS, CENTER, MAX_DIST, WORLD_SIZE_PIX
    S = s
    _COLLISION_POINTS = [(x+S//2,y+S//2) for x,y in _COLLISION_POINTS]
    _COLLISION_POINTS = tuple(_COLLISION_POINTS)
    CENTER = Vector2(S//2,S//2)
    WORLD_SIZE_PIX = Vector2(WORLD_SIZE)*S
    MAX_DIST = WORLD_SIZE_PIX/2

def set_radius(load, free):
    print("setting radius", load, free)
    global RADIUS_FREE, RADIUS_LOAD, MAX_CHUNKS
    assert load > 1
    assert free >= load
    RADIUS_LOAD = load
    RADIUS_FREE = free
    MAX_CHUNKS = int(3.14*RADIUS_FREE**2) + 1

def set_approx_memory_usage(megabytes, load=None):
    global RADIUS_FREE, RADIUS_LOAD, MAX_CHUNKS, USE_LOADER
    c = get_memory_per_chunk()
    if megabytes/c < 1:
        USE_LOADER = False
        return
    if load is not None:
        RADIUS_LOAD = load
    RADIUS_FREE = int((1./3.14 * (megabytes/c - 1))**0.5)
    if RADIUS_FREE < 2:
        USE_LOADER = False
        return
    RADIUS_FREE = max(RADIUS_FREE,2)
    RADIUS_LOAD = min(RADIUS_LOAD,RADIUS_FREE)
    set_radius(RADIUS_LOAD, RADIUS_FREE)
    USE_LOADER = True

def emerge(color, n, beg_alpha, final_alpha, invert=False):
    s = pygame.Surface((S,S))
    s.fill(color)
##    s.convert_alpha()
    if invert:
        s.set_alpha(final_alpha)
        rng = np.linspace(final_alpha,beg_alpha,n,dtype=int)
    else:
        s.set_alpha(beg_alpha)
        rng = np.linspace(beg_alpha,final_alpha,n,dtype=int)
    for i in rng:
        s.set_alpha(i)
##        screen.blit(s)
        yield s

def nothing():
    pass

def get_camera_type():
    import terrain
    if BISURFACE:
        return terrain.CameraBisurface
    else:
        return terrain.Camera

import time
import numpy as np
import pygame
from pygame.math import Vector2
import thorpy
import terrain, core, parameters
from wind import Wind
from ship import Ship
import village
import gui
import scenario
import sound
import savemanager
import fx



pygame.mixer.pre_init(44100, 16, 2, 4096) #frequency, size, channels, buffersize
pygame.mixer.init(frequency=22050, size=-16, channels=2, buffer=512)
##SEED = 18
##SEED = 10131425
##SEED = int(save["cam"]["seed"])
##SEED = 800
SEED = 66
##SEED = 0

S = terrain.S
parameters.set_S(S)


METADATA_PATH = "./metadata" #create a file for storing data on application
mdm = thorpy.MetaDataManager()
mdm.read_data(METADATA_PATH)
app = thorpy.Application((S,S))
mdm.load_font_data(METADATA_PATH)
gui.show_loading()
gui.playing() #set key delay
thorpy.set_theme("human")
screen = thorpy.get_screen()
e_bckgr = thorpy.Ghost.make()
sound.play_random_music()
terrain.cache()

savefile=gui.launch_main_menu() #xxx
climate = terrain.Climate(0)

if savefile:
    gui.show_loading()
    sm = savemanager.SaveManager(savefile)
    SEED = int(sm.d["cam"]["seed"])
    sm.load_parameters()

Camtype=parameters.get_camera_type()
cam = Camtype(chunk=(0,0), pos=(0,0), seed=SEED,
                                            world_size=parameters.WORLD_SIZE)

core.load_images()
core.compute_parameters()

wind = Wind((-1.,-1.),(1.,1.),(-1., -1.),(1.,1.),(10000,10000))
game = core.Game(cam, wind, climate, e_bckgr)

game.set_ship(Ship(mass=0.3, maxvel=3., life=1., captain=None))
game.refresh_controllables()

reac_time = thorpy.ConstantReaction(thorpy.constants.THORPY_EVENT, game.reac_time, {"id":thorpy.constants.EVENT_TIME})
reac_keydown = thorpy.Reaction(pygame.KEYDOWN, game.reac_keydown)
e_bckgr.add_reaction(reac_keydown)
e_bckgr.add_reaction(reac_time)

gu = gui.GUI(game)

if not savefile:
    #configure new game
    varset = gui.game_parameters_menu()
    #
    #difficulty : TREASURE_PROB, MAX_FLAG, FOOD_PER_TURN, MAX_CAMPS, OASIS_PROB
    difficulties = {"easy":(1., 10, 1, 5, 1.),
                    "medium":(0.8, 5, 1, 3, 0.8),
                    "hard":(0.4, 3, 1, 1, 0.7)}
    seed = varset.get_value("seed")
##    seed = 42877
    parameters.WORLD_SIZE = varset.get_value("worldx"),varset.get_value("worldy")
    parameters.set_world_size(parameters.WORLD_SIZE)
    parameters.SEASON_MOD_DAYS = varset.get_value("seasonmod")
    diff = difficulties[varset.get_value("difficulty")]
    parameters.TREASURE_PROB = diff[0]
    parameters.MAX_FLAGS = diff[1]
    parameters.FOOD_PER_TURN = diff[2]
    parameters.MAX_CAMPS = diff[3]
    parameters.OASIS_PROB = diff[4]
    cam.reset(seed)
    game.next_season = parameters.SEASON_MOD_DAYS
    core.perigeo.img_pos = Vector2(parameters.WRECK_COORD)*parameters.S

intro = scenario.get_intro_text()
core.instructions = scenario.get_instructions()
game.instructions = core.instructions

if not savefile:
    #actual game
    m = thorpy.Menu(intro)
    m.play()
    gui.show_loading()
    ##image = thorpy.load_image("bottle.png")
    image = thorpy.load_image("message_in_a_bottle_by_solid_pawn.png")
    image = pygame.transform.scale(image, (parameters.S,parameters.S))
    screen.blit(image,(0,0))
    pygame.display.flip()
    m = thorpy.Menu(core.instructions)
    m.play()
    #xxx
    game.choose_ship()
    game.choose_astronomer()
    game.choose_hunter()
    game.choose_captain()
    game.set_ship(game.ship)
    game.refresh_controllables()
    app.fill((0,0,0))
    pygame.display.flip()
    game.e_x.set_text("0")
    game.e_y.set_text("0")
    game.journal.add_entry("Exploration begins", "Leaving departure city. We are optimistic and look forward to sail around the world.")

parameters.USE_LOADER = False
if parameters.USE_LOADER:
    print("Memory usage per chunk =", parameters.get_memory_per_chunk(), "Mo")
    print("Total memory usage for chunks =", parameters.get_memory_all_chunks(), "Mo")
    print("Max chunk in memory =", parameters.MAX_CHUNKS)
    print("Load radius =", parameters.RADIUS_LOAD)
    print("Free radius =", parameters.RADIUS_FREE)
    game.load_chunks()

fx.set_rain_smokegen()

if savefile:
    sm.load_game(game)
    core.perigeo.img_pos -= game.campos
    core.refresh_imgs_ship(game.ship.model)
    game.set_ship_imgs()
else:
    game.init_ship_pos()

# ##############################################################################
##thorpy.application.SHOW_FPS = True
m = thorpy.Menu([e_bckgr],fps=parameters.FPS)
m.play()

app.quit()

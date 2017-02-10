# -*- coding: utf-8 -*-
import sys
import math
import numpy as np
import pygame
from pygame.math import Vector2
import thorpy
from character import Character
import parameters
import gui
from gui import LifeBar
from statistics import Statistics
from controllable import FoodStock, Flag, Tile, Treasure
from village import try_building_structure, force_build_structure
import initializer
import colorscale
from wind import Wind
import scenario
import fx
import sound
import savemanager
import os
##import gui

JUNK = 1
CARAVEL = 2
SHIP_TYPE = JUNK
SHIP_STR = str(SHIP_TYPE)

SHIP = 0

ASTRO = 1
HUNT = 2
CAP = 3


LEFT = Vector2(-1,0)
RIGHT = Vector2(1,0)
UP = Vector2(0,-1)
DOWN = Vector2(0,1)

SIDE_LEFT = 0*parameters.MOD_PHASE_SHIP
SIDE_RIGHT = 1*parameters.MOD_PHASE_SHIP
SIDE_UP = 2*parameters.MOD_PHASE_SHIP
SIDE_DOWN = 3*parameters.MOD_PHASE_SHIP

left, right, up, down = None, None, None, None
compass, girouette = None, None
houses = []
oasises = []
firs = []
cloud = None
tent = None
star = None
flag = None
treasure = None
perigeo = None
thermo = None
imgs_ship = {}
thermo_fluid_rect = pygame.Rect(9,3,5,39)
imgs_arrows = []

girouette_pos = None
compass_pos = None
thermo_pos = None
fluid_pos = None
##arrows_pos = None

instructions = None

sounds = sound.get_sounds()
##musics = sound.get_musics()

def refresh_imgs_ship(model):
    global left, right, up, down
    left, right, up, down = imgs_ship[model]

class Season:

    def __init__(self, name, colorscale, level, temp_shift, text):
        self.name = name
        self.colorscale = colorscale
        self.level = level
        self.temp_shift = temp_shift
        self.text = text

class Journal:

    def __init__(self, game):
        self.entries = []
        self.game = game

    def add_entry(self, title, text):
        if self.game.a.life > 0:
            coord = self.game.get_coord_journal()
        else:
            coord = "(?,?)"
        entry = (title,
                             self.game.day,
                             coord,
                             self.game.alt_text,
                             self.game.temp,
                             text)
        print("entry",entry)
        self.entries.append(entry)

def distance_to_center(pos):
    return Vector2(pos[0],pos[1]).distance_to(parameters.CENTER)

def load_images():
    #
    global left, right, up, down, compass, girouette, thermo, houses, flag, tent, imgs_ship, star, perigeo, treasure
    perigeo_img = thorpy.load_image("boat_perigeo.png",(255,255,255))
    perigeo = Tile(perigeo_img, Vector2(parameters.WRECK_COORD)*parameters.S)
    #
    lc = thorpy.load_image("boat_left_2.png",(255,255,255))
    rc = thorpy.load_image("boat_right_2.png",(255,255,255))
    uc = thorpy.load_image("boat_rear_2.png",(255,255,255))
    dc = thorpy.load_image("boat_front_2.png",(255,255,255))
    #
    lj = thorpy.load_image("boat_left_1.png",(255,255,255))
    rj = thorpy.load_image("boat_right_1.png",(255,255,255))
    uj = thorpy.load_image("boat_rear_1.png",(255,255,255))
    dj = thorpy.load_image("boat_front_1.png",(255,255,255))
    #
    left,right,up,down = (lj,rj,uj,dj)
    imgs_ship[CARAVEL] = (lc,rc,uc,dc)
    imgs_ship[JUNK] = (lj,rj,uj,dj)
##    left = thorpy.load_image("boat_left_"+SHIP_STR+".png",(255,255,255))
##    right = thorpy.load_image("boat_right_"+SHIP_STR+".png",(255,255,255))
##    up = thorpy.load_image("boat_rear_"+SHIP_STR+".png",(255,255,255))
##    down = thorpy.load_image("boat_front_"+SHIP_STR+".png",(255,255,255))
    #
    star = thorpy.load_image("star.png", (255,255,255))
    compass = thorpy.load_image("r6.png",(255,255,255))
    compass.set_alpha(160)
    thermo = thorpy.load_image("thermometer.png",(255,255,255))
    for i in range(2):
        houses.append(thorpy.load_image("house"+str(i)+".png", (255,255,255)))
        oasises.append(thorpy.load_image("oasis"+str(i)+".png", (255,255,255)))
        firs.append(thorpy.load_image("fir"+str(i)+".png", (255,255,255)))
    tent = thorpy.load_image("tent2.png",(255,255,255))
    flag = thorpy.load_image("flag.png",(255,255,255))
    i = 0
    for i in range(6):
        imgs_arrows.append(thorpy.load_image("arrow"+str(i)+".png", (255,255,255)))
    treasure = thorpy.load_image("treasure.png",(255,255,255))


def compute_parameters():
    global compass_pos, girouette_pos, thermo_pos, fluid_pos
    w,h = compass.get_size()
    margin = 20
    compass_pos = (parameters.S-w-margin,20+margin)
    girouette_pos = (compass_pos[0]+w//2-1, compass_pos[1]+h//2-1)
    r = thermo.get_rect()
    r.centerx = girouette_pos[0]
    r.y = compass_pos[1] + h//2 + parameters.GIROUETTE_LENGTH + margin
    thermo_pos = r.topleft
    fluid_pos = (thermo_pos[0]+10, thermo_pos[1]+3)

class Game:

    def __init__(self, cam, wind, climate, element):
        summer = Season("Summer", colorscale.get_summer(), parameters.SUMMER_LEVEL, 2,
                        "Summer comes in 5 days.\nHigh temperatures are back again, and ices will melt.")
        winter = Season("Winter", colorscale.get_winter(), parameters.WINTER_LEVEL, -20,
                        "Winter comes in 5 days.\nBe sure that the ship is far from the lands, or it will become captive of the ices")
        self.clouds = []
        for i in range(3):
            img = thorpy.load_image("clouds"+str(i)+".png",(0,0,0))
            img.set_alpha(parameters.CLOUD_ALPHA)
            self.clouds.append(img)
        #characters
        a = Character("Astronomer", parameters.A_COLOR)
        a.death_text = "Without astronomer, we won't know our position anymore..."
        h = Character("Hunter", parameters.H_COLOR)
        h.hunting = 0.6
        h.death_text = "Without hunter, we will have troubles in finding extra food..."
        c = Character("Captain",  parameters.C_COLOR)
        c.ship_skill = 0.5
        c.death_text = "Without captain, the ship will be slower and weaker against rocks..."
        #
        self.save = None
        self.saved = False
        self.a, self.h, self.c = a, h, c
        self.cam = cam
        self.wind = wind
        self.climate = climate
        self.screen = thorpy.get_screen()
        self.element = element
        self.peaks = {}
        self.cam.game = self
        self.gui_pos = np.zeros(2)
        self.campos = np.array([float(self.cam.pos[0]),float(self.cam.pos[1])])
        self.ship = None
        self.input_direction = Vector2()
        self.direction = False
        self.i = 0
        self.tx, self.ty = None, None
        self.controlled = None
        self.controllables = None
        self.last_key_action = 0
        self.current_wind_draw = None
        self.height = 0
        self.alt_text = 0
        self.temp = 0
        self.temp_pix = 0
        self.temp_text = 0
        self.day = 0
        gui.set_game_gui(self, compass_pos, compass, thermo_pos, thermo) #declare attributes
        self.pos_int = Vector2()
        #
        self.refresh_ship_life = True
        self.stats = Statistics(self)
        self.can_board = False
        self.near_village = None
        self.near_camp = None
        self.near_forest = None
        self.can_flag = False
##        self.villages = {(0,0):Village((houses[0],houses[1]),Vector2(100,100),12)}
        self.villages = []
        self.oasises = []
##        self.firs = []
        self.monitor = gui.AlertMonitor(self)
        self.aboard = True
        self.swimming = False
        self.flags = []
        self.near_flag = None
        self.journal = Journal(self)
        self.living_chars = list(self.chars())
        self.building_map = False
        self.collision_factor = 0.
        self.collision_factor_summer = 0.
        self.can_camp = False
        self.ncamps = 0
        self.infinite_stock = FoodStock(100000000000)
        self.infinite_stock.food = 1000000000
        self.side = 0
        #
        self.storm = None
        self.storm_duration = 0
        self.storms = np.random.randint(2,10000,400).tolist()
##        self.storms[0] = 1
        self.rain = fx.Rain(self, 150)
        self.snow = fx.Rain(self, 150, thorpy.load_image("snowflake.png",(0,0,0)))
        self.falls = self.rain
        self.seasons = [summer, winter]
        self.season_idx = 0
        self.set_season(self.season_idx)
        self.next_season = parameters.SEASON_MOD_DAYS
        self.instructions = instructions
        self.does_perigeo = False
        self.score = -1
        #
        self.n_hunt = parameters._INIT_N_HUNT
        self.is_winter = False
        self.treasures = []
        self.treasures_taken = []
        self.treasures_put = []
        self.near_treasure = None
        self.waiting = False
##        self.e_wait = gui.LifeBar("Waiting next season",size=(300,50))
##        self.e_food_wait = gui.LifeBar("Food",size=(300,50))
##        thorpy.store(self.screen.get_rect(), [self.e_wait,self.e_food_wait])
##        newday = None

    def refresh_camera(self):
        Camtype = parameters.get_camera_type()
        cam = Camtype(chunk=self.cam.chunk, pos=self.cam.pos, seed=self.cam.seed,
                        world_size=self.cam.world_size)
        cam.villages = self.cam.villages
        cam.chunk = self.cam.chunk
        cam.pos = self.cam.pos
        self.cam = cam
        self.cam.game = self

    def show_end(self):
        scenario.launch(self.gui.get_stats())
        self.cam.show(self.screen)
        self.blit_things()
        pygame.display.flip()
        self.reac_j()
        thorpy.functions.quit_menu_func()
        print("FINI")
##        thorpy.get_application().quit()
##        sys.exit()

    def get_coord_journal(self):
        return "("+self.e_x.get_text() +","+ self.e_y.get_text()+")"

    def choose_ship(self):
        self.cam.show(self.screen)
        self.blit_villages()
        pygame.display.flip()
        global left,right,up,down
        lc = imgs_ship[CARAVEL][0]
        lj = imgs_ship[JUNK][0]
        carmass = 0.2
        junmass = 0.6
        cm = 1. - carmass
        jm = 1. - junmass
        ship_skills = ({"Maneuverability":cm, "Velocity":0.6, "Robustness":0.6},
                        {"Maneuverability":jm, "Velocity":0.8, "Robustness":1.})
        v = initializer.get_controllable_choice("Choose a ship", [lc, lj],
                                             ["Caravel", "Junk"],
                                             ship_skills,
                                             "Ships with low mass are easier to maneuver. Since sailing is much faster than swimming, ship is a precious tool for your exploration. Don't broke it.",
                                             "Buy",
                                             star)
        self.ship.mass = 1. - ship_skills[v]["Maneuverability"]
        self.ship.maxvel = ship_skills[v]["Velocity"]
        self.ship.weakness = 1. - ship_skills[v]["Robustness"]
        if v == 0:
            left, right, up, down = imgs_ship[CARAVEL]
            self.ship.model = CARAVEL
        else:
            left, right, up, down = imgs_ship[JUNK]
            self.ship.model = JUNK

    def choose_astronomer(self):
        self.cam.show(self.screen)
        self.blit_villages()
        pygame.display.flip()
        skills = [{"Health":0.6, "Hunting":0.6, "Sailing":0.6},
                    {"Health":1., "Hunting":0.2, "Sailing":0.2}]
        a_img = pygame.Surface(self.a.img.get_size())
        a_img.fill((255,255,255))
        a_img.blit(self.a.img,(0,0))
        a_img = a_img.convert_alpha()
        a_img.set_colorkey((255,255,255))
        v = initializer.get_controllable_choice("Choose an astronomer", [a_img,a_img],
                                             ["Johannes", "Tycho"],
                                             skills,
                                             "Astronomers are able to deduce position from the stars. With no astronomer, explorers are blind.",
                                             star=star)
        self.a.weakness = 1.-skills[v]["Health"]
        self.a.hunting = skills[v]["Hunting"]
        self.a.ship_skill = skills[v]["Sailing"]

    def choose_hunter(self):
        self.cam.show(self.screen)
        self.blit_villages()
        pygame.display.flip()
        skills = [{"Health":0.8, "Hunting":0.8, "Sailing":0.2},
                    {"Health":0.6, "Hunting":1.0, "Sailing":0.2}]
        a_img = pygame.Surface(self.h.img.get_size())
        a_img.fill((255,255,255))
        a_img.blit(self.h.img,(0,0))
        a_img = a_img.convert_alpha()
        a_img.set_colorkey((255,255,255))
        v = initializer.get_controllable_choice("Choose a hunter", [a_img,a_img],
                                             ["Gunter", "Gaston"],
                                             skills,
                                             "Hunters are able to find food in nature much faster than any other unit.",
                                             star = star)
        self.h.weakness = 1. - skills[v]["Health"]
        self.h.hunting = skills[v]["Hunting"]
        self.h.ship_skill = skills[v]["Sailing"]

    def choose_captain(self):
        self.cam.show(self.screen)
        self.blit_villages()
        pygame.display.flip()
        skills = [{"Health":0.8, "Hunting":0.2, "Sailing":0.8},
                  {"Health":0.6, "Hunting":0., "Sailing":1.0}]
        a_img = pygame.Surface(self.c.img.get_size())
        a_img.fill((255,255,255))
        a_img.blit(self.c.img,(0,0))
        a_img = a_img.convert_alpha()
        a_img.set_colorkey((255,255,255))
        v = initializer.get_controllable_choice("Choose a captain",
                                             [a_img,a_img],
                                             ["Hook", "Newton"],
                                             skills,
                                             "Captains are good at sailing. With no captain, transport by ship will be a pain.",
                                             star = star)
        self.c.weakness = 1. - skills[v]["Health"]
        self.c.hunting = skills[v]["Hunting"]
        self.c.ship_skill = skills[v]["Sailing"]

    def get_clim_coord(self):
        world_level = self.cam.chunk
        chunk_level = self.cam.pos%parameters.S / parameters.S
        return (world_level + chunk_level) * parameters.S / self.cam.world_size

    def chars(self):
        yield self.a
        yield self.h
        yield self.c

    def set_ship(self, ship):
        self.ship = ship
        self.controlled = ship
        self.stock = ship
        self.ship.captain = self.c
        self.set_ship_imgs()

    def set_ship_imgs(self):
        self.ship.img = left
        self.ship.normal_imgs = self.ship.build_imgs(8, (left,right,up,down))
        self.ship.storm_imgs = self.ship.build_imgs(25, (left,right,up,down))
        self.ship.imgs = self.ship.normal_imgs

    def init_ship_pos(self):
        collisions = self.cam.show(self.screen)
        collision_factor = self.controlled.compute_collision_factor(collisions, parameters.WATER_LEVEL)
        while collision_factor > 0.5:
            self.set_cam_pos(self.campos-(10,0))
            self.refresh_controlled
            collisions = self.cam.show(self.screen)
            pygame.display.flip()
            collision_factor = self.controlled.compute_collision_factor(collisions, parameters.WATER_LEVEL)

    def refresh_controllables(self):
        self.controllables = [self.ship,self.a,self.h,self.c]
        self.refresh_controlled()

    def refresh_controlled(self):
        w,h = self.controlled.img.get_size()
        x = (parameters.S-w)//2
        y = (parameters.S-h)//2
        self.controlled.img_pos = Vector2(x,y)

    def board_ship(self):
        self.set_cam_pos(self.ship.img_pos +\
                                    Vector2(self.ship.img.get_size())/2)
        self.controlled = self.ship
        self.ship.refood_from(self.stock)
        self.stock = self.ship
        self.aboard = True


    def leave_ship(self):
        self.ship.velocity = Vector2()
        self.controlled = self.living_chars[0]
        for c in self.living_chars:
            c.aboard = False
            if c is not self.controlled:
                c.img_pos = parameters.CENTER + np.random.random(2)*20
        self.stock = FoodStock(len(self.living_chars))
        self.stock.refood_from(self.ship)
        self.stock.name = "Explorers"
        self.aboard = False
        self.ship.anchor()

    def reac_space(self):
        if self.aboard: #leave ship
            self.leave_ship()
        else: #enter ship
            if self.can_board:
               self.board_ship()
            else:
                sounds.cannot.play()
                self.monitor.launch_failure_alert("Too far from ship for boarding...")
        self.refresh_controlled()

    def reac_e(self):
        if self.near_village:
            if self.save:
                saved = self.save.villages.get(self.near_village.id)
                if saved:
                    print("previous",saved,self.near_village.id)
                    food,type_,pos = saved
                    if type_ == "v" or type_ == "o":
                        self.near_village.set_food(food)
            gui.manage_stocks(self.stock, self.near_village)
            self.e_food.set_life(self.stock.food/self.stock.max_food)

    def get_near_flag(self):
        for f in self.flags:
            if distance_to_center(f.img_pos) < parameters.READ_FLAG_DIST:
                return f

    def get_near_treasure(self):
        for t in self.treasures:
            if distance_to_center(t.img_pos) < parameters.READ_FLAG_DIST:
                return t

    def reac_r(self):
        if self.near_flag:
            take = gui.read_flag(self.near_flag)
            if take:
                self.flags.remove(self.near_flag)

    def reac_t(self):
        if self.near_treasure:
            take = gui.read_treasure(self.near_treasure)
            if take:
                self.treasures.remove(self.near_treasure)
                food = self.near_treasure.food
                nhunt = self.near_treasure.n_hunt
                self.n_hunt += nhunt
                if self.n_hunt > parameters._INIT_N_HUNT : self.n_hunt = parameters._INIT_N_HUNT
                self.stock.add_food(food)
                self.treasures_taken.append(self.near_treasure.chunk)

    def plant_flag(self, pos, title, text):
        flagtile = Flag(flag, pos, title, text)
        self.flags.append(flagtile)

    def reac_f(self):
        if self.near_flag is None:
            if self.can_flag:
                sounds.ok.play()
                pos = Vector2(self.controlled.img_pos)
                flagtile = Flag(flag, pos, title="Flag "+str(len(self.flags)))
                cancel = gui.plant_flag(flagtile)
                if not cancel:
                    self.flags.append(flagtile)
                    self.journal.add_entry(flagtile.title, flagtile.text)
            else:
                sounds.cannot.play()
                if len(self.flags) >= parameters.MAX_FLAGS:
                    self.monitor.launch_failure_alert("You have no flag left. Take flag somewhere else.")
                else:
                    self.monitor.launch_failure_alert("You cannot plant flag here")
        elif self.can_flag:
            sounds.cannot.play()
            self.monitor.launch_failure_alert("You are too close from a flag to plant another one")


    def reac_j(self):
        gui.get_journal(self)

    def autosave(self):
        if self.saved:
            fn = self.save.fn
        else:
            i = len([f for f in os.listdir("./") if f.startswith("save") and f.endswith(".dat")])
            fn = "save"+str(i)+".dat"
            self.saved = True
        savemanager.save_game(fn,self)

    def reac_x(self):
        ok_food = self.stock.food < parameters.CRITICAL_FOOD
        ok_n = len(self.living_chars) > 1
        if ok_n and ok_food:
            sound.play_music("before winter")
            sounds.gong.play()
            choice = gui.get_cannibalism(self)
            if choice:
                sounds.scream.play()
                if choice == "a":
                    m = self.a
                if choice == "c":
                    m = self.c
                if choice == "h":
                    m = self.h
                m.life = -100000
                for c in self.living_chars:
                    self.stock.add_food(parameters.FOOD_CANNIBAL)
        else:
            sounds.cannot.play()
            if not ok_n:
                self.monitor.launch_fading_alert("The only survivor does not want to eat himself...")
            else:
                self.monitor.launch_fading_alert("In crew members' opinion, there is too much food left to cannibalize each other.")


    def next_music(self):
        sound.play_random_music()

##    def get_hunt_days(self):
##        if self.h.life > 0:
##            c = self.h.hunting
##        else:
##            c = self.living_chars[0].hunting
##        #use temp_pix to always have positive value
##        return (1.*self.temp_pix/10. + 1.*self.height*2)*parameters.HUNT_FACTOR*(1.2-c)

    def advance_days(self, delta):
        for i in range(delta):
            self.set_next_day()

    def set_next_day(self):
        self.storm_duration -= 1
        self.next_season -= 1
        if self.next_season == 5 and not self.waiting:
            next_idx = (self.season_idx+1)%len(self.seasons)
            thorpy.launch_blocking_alert(self.seasons[next_idx].text)
            if self.seasons[next_idx].name == "Winter":
                sound.play_music("before winter")
        elif self.next_season == 0:
            self.set_next_season()
            self.next_season = parameters.SEASON_MOD_DAYS
        self.day += 1

    def hunt_success(self):
        temp_factor = (self.temp+15)/100.
        print("temp factor", temp_factor)
        #
        hunt_factor = max([c.hunting for c in self.living_chars])
        print("hunt factor", hunt_factor)
        #
        factor = 0.6*hunt_factor + 0.4*temp_factor
        print("prefactor", factor)
        if self.near_forest: #add bonus
            factor += 0.2
        factor = max(factor, parameters.MIN_HUNT_PROB)
        factor = min(factor, parameters.MAX_HUNT_PROB)
        print("     final factor", factor)
        return np.random.random() < factor

    def reac_h(self):
        if self.near_camp:
            if self.n_hunt > 0:
                hunt = gui.want_to_hunt()
                if hunt:
                    self.n_hunt -= 1
                    if self.hunt_success():
                        self.stock.refood_from(self.infinite_stock)
                        self.infinite_stock.food += self.stock.food # :)
                        self.monitor.launch_success_alert("Hunting was a sucess!")
                    else:
                        self.monitor.launch_failure_alert("Failed to find any form of life here... Except the crew.")
            else:
                sounds.cannot.play()
                self.monitor.launch_failure_alert("No arrows left. You can't hunt...")

        else:
            sounds.cannot.play()
            self.monitor.launch_failure_alert("You need a camp to hunt !")

    def reac_p(self):
        near = None
        if self.near_village:
            near = self.near_village
        elif self.near_camp:
            near = self.near_camp
        if near and not self.aboard and not(self.stock.food < parameters.CRITICAL_FOOD):
            if thorpy.launch_binary_choice("Wait in the " + near.name + " until the next season / until the food level is critical ?"):
                self.waiting = True
                while self.waiting:
##                    self.reac_time()
                    self.wait()
                    self.stock.refood_from(near)
                    if self.stock.food < parameters.CRITICAL_FOOD:
                        thorpy.launch_alert("Your food level is critical...\n Waiting mod is now off.")
                        break
        else:
            sounds.cannot.play()
            self.monitor.launch_failure_alert("You need to be in a camp/village and to have enough food to wait !")

##        if self.near_camp and not self.aboard:
##            days = round(self.get_hunt_days(),1)
##            if days < 1000:
##                hunt = gui.hunt(days)
##                if hunt:
##                    for d in range(self.day, int(self.day+days)):
##                        self.set_next_day()
##                    self.stock.refood_from(self.infinite_stock)
##                    self.infinite_stock.food += self.stock.food
##                    print("Delta days", days/parameters.DAY_FACTOR)
##                    self.i += days/parameters.DAY_FACTOR
####                    self.reac_time_low()
##            else:
##                self.monitor.launch_fading_alert("The harsh climate here won't allow to find enough food to survive")
##                sounds.cannot.play()

    def build_camp(self):
        force_build_structure(self, [tent,tent], None, None,
                                len(self.living_chars), type_="c")
        self.ncamps += 1

    def reac_c(self):
        if self.near_camp:
            uncamp = gui.uncamp()
            if uncamp:
                sounds.ok.play()
                self.stock.refood_from(self.near_camp)
                self.villages.remove(self.near_camp)
                self.ncamps -= 1
        elif self.can_camp:
            if (self.near_village is None) or (self.near_forest is not None):
                if self.ncamps < parameters.MAX_CAMPS:
                    sounds.ok.play()
                    self.build_camp()
                else:
                    sounds.cannot.play()
                    self.monitor.launch_failure_alert("You already used your "+\
                                                    str(parameters.MAX_CAMPS)+\
                                                    " tents. Uncamp somewhere to get tents.")
            else:
                sounds.cannot.play()
                self.monitor.launch_failure_alert("Too close to "+self.near_village.name+"... go further.")
        elif not self.can_camp:
            sounds.cannot.play()
            self.monitor.launch_failure_alert("You can't camp on water or melting ice")


    def reac_keydown(self, e):
        if self.i > self.last_key_action + parameters.DELTA_SPACE_I:
            self.last_key_action = self.i
            if e.key == pygame.K_SPACE:
                self.reac_space()
            elif e.key == pygame.K_e:#exchange food
                self.reac_e()
            elif e.key == pygame.K_f:#flag
                self.reac_f()
            elif e.key == pygame.K_t:#flag
                self.reac_t()
            elif e.key == pygame.K_r:#read flag
                self.reac_r()
            elif e.key == pygame.K_j:#journal
                self.reac_j()
            elif e.key == pygame.K_c:#camp
                self.reac_c()
            elif e.key == pygame.K_h:#hunt
                self.reac_h()
            elif e.key == pygame.K_p:#wait
                self.reac_p()
            elif e.key == pygame.K_x:#kill crew
                self.reac_x()

    def process_direction(self):
        pressed = pygame.key.get_pressed()
        if pressed[pygame.K_RIGHT]:
            self.input_direction = RIGHT
            self.side = SIDE_RIGHT
            self.direction = True
        if pressed[pygame.K_LEFT]:
            self.input_direction = LEFT
            self.side = SIDE_LEFT
            self.direction = True
        if pressed[pygame.K_UP]:
            self.input_direction = UP
            self.side = SIDE_UP
            self.direction = True
        if pressed[pygame.K_DOWN]:
            self.input_direction = DOWN
            self.side = SIDE_DOWN
            self.direction = True

    def get_relative_position(self, absolute_position):
        """absolute_position = positive position = chunk*S"""
        delta = absolute_position - self.campos
        return delta


    def set_cam_pos(self, pos):
        delta = pos - self.controlled.img_pos
        self.campos += delta
        self.cam.pos = np.array(self.campos,dtype=int)
        self.refresh_img_pos(delta)
        self.cam.show(self.screen)

    def kill_member(self,c):
        c.life = -10000
        thorpy.launch_blocking_alert(c.name+" is dead.", self.element)
        self.journal.add_entry(c.name+"'s death.", c.death_text)

    def refresh_life_and_food(self):
        if self.ship.life <= 0:
            if not self.ship.dead:
                thorpy.launch_blocking_alert("Ship's damages are too high. It will now derive with wind in the oceans. You can disembark.")
                self.ship.dead = True
        #####################################refresh characters life
        temp_bad = abs(parameters.TEMP_IDEAL - self.temp) / parameters.TEMP_MAX
        new_living = []
        for c in self.living_chars:
            refresh = c.refresh_life(self.stock, temp_bad)
            if refresh:
                self.echars[c].set_life(c.life)
                if c.life <= 0:
                    self.kill_member(c)
                else:
                    new_living.append(c)
            else:
                new_living.append(c)
        if not new_living:
            print("Game over")
            thorpy.launch_blocking_alert("No one survived the terrible expedition.\nGame over")
            self.journal.add_entry("This is the end.", "If someone finds this log. Please bring it back to our city.")
            self.show_end()
            return
        if self.ship.captain.life <= 0:
            self.ship.captain = new_living[0]
        if not self.aboard:
            if self.controlled.life <= 0:
                self.controlled = new_living[0]
                self.refresh_controlled()
        self.living_chars = new_living
        self.e_food.set_life(self.stock.food/self.stock.max_food)
        if self.i%parameters.MOD_VILLAGE_FOOD_REGEN == 0:
            for v in self.villages:
                if v.food < v.max_food:
                    v.food += int(parameters.MAX_VSF*v.n/10)
        ################################################################

    def wait(self):
        if self.i % parameters.MOD_LOW == 0:
            self.reac_time_low()
        if self.i % parameters.MOD_LIFE == 0:
            self.refresh_life_and_food()
##            screen.fill((255,255,255))
            self.cam.show(self.screen)
            self.blit_things()
            pygame.display.flip()
        if self.storm:
            self.falls.refresh()
            self.falls.blit()
        #
        self.i += 1
        #

    def reac_time_low(self):
##        if self.i > 150:
##            self.a.life = -10
##        if self.i > 300:
##            self.c.life = -10
##        if self.i > 1000:
##            self.h.life = -10
##        print(self.cam.chunk)
        if not pygame.mixer.music.get_busy():
            self.next_music()
        if perigeo.img_pos.distance_to(parameters.CENTER) < 50:
            if not self.does_perigeo:
                sounds.perigeo.play()
                gui.show_loading()
                scenario.launch_perigeo_text()
                self.does_perigeo = True
                self.journal.add_entry("Found Perigeo's wreckage!!!","We can now go back to civilization.")
        if self.does_perigeo:
            if self.get_distance_from_0() < parameters.S:
                if self.score < 0:
                    self.score = self.day
                    self.journal.add_entry("End of the trip.", "There are no words to describe our pride and joy.\nWe are back to our departure point.")
                    gui.show_loading()
                    scenario.launch_end_text(self.score)
    ##                self.show_end()
        #checkpoints
        for c in self.controllables:
            c.refresh_last_position(self.cam)
        #temperature
        self.refresh_temperature()
        self.temp_pix = self.temp*parameters.TNORM_A + parameters.TNORM_B
        self.e_temp.set_text(str(self.temp_text)+" C ")
        #coordinates
        alt_text = int((self.height-parameters.SUMMER_LEVEL)*parameters.FACTOR_ALT)
        self.alt_text = alt_text
        self.e_alt.set_text("Alt.: "+str(alt_text)+ " m")
##        if self.a.life > 0:
##            x,y = self.cam.chunk
##        else:
##            x,y = "?", "?"
        if self.a.life > 0:
            self.gui_pos = (self.campos%parameters.WORLD_SIZE_PIX)/10.
            xint = int(self.gui_pos[0])
            yint = int(self.gui_pos[1])
            x = str(xint)
            y = str(yint)
        else:
            x,y = "?", "?"
        self.e_x.set_text("X: "+x)
        self.e_y.set_text("Y: "+y)
##        self.pos_int += (xint,yint)
        #life and food
        if self.refresh_ship_life:
            self.e_life_ship.set_life(self.ship.life)
        #time
        newday = int(self.i * parameters.DAY_FACTOR)
        if newday > self.day:
            self.set_next_day()
##            self.advance_days(newday-self.day) #to be validated
            if newday in self.storms:
                if self.storm is None:
                    if parameters.BISURFACE:
                        self.cam.clouds = []
                    sound.play_music("storm", 10)
                    self.storm_duration = np.random.randint(2,10)
                    F = 8.
                    self.storm = Wind((-F,-F),(F,F),(-1., -1.),(1.,1.),(1000,1000))
                    self.ship.imgs = self.ship.storm_imgs
                    if self.seasons[self.season_idx].name == "Winter":
                        self.falls = self.snow
                    else:
                        self.falls = self.rain
            elif self.storm_duration <= 0:
                if self.storm is not None:
                    if parameters.BISURFACE:
                        self.cam.init_clouds()
                    sound.play_random_music()
                    self.storm = None
                    self.ship.imgs = self.ship.normal_imgs
            self.day = newday
            self.e_clock.set_text("Day "+str(newday))
        #
        if self.i > 0:
            self.stats.refresh()
        d = (self.ship.img_pos+Vector2(self.ship.img.get_size())/2).distance_to(parameters.CENTER)
        self.can_board = d < parameters.BOARDING_DISTANCE
        self.can_camp = (self.collision_factor_summer == 0) and (not self.aboard)

    def set_season(self,idx):
        s = self.seasons[idx]
        self.cam.set_colorscale(s.colorscale)
        parameters.WATER_LEVEL = s.level
        for couple in self.cam.saved_chunks.values(): #reset images
            couple[1] = None
        #refresh oasis food
        if s.name == "Winter":
            self.is_winter = True
            for i in range(len(self.villages)-1,-1,-1):
                if self.villages[i].type == "o":
                    self.villages.pop(i)
        else:
            self.is_winter = False
            self.villages += self.oasises

    def set_next_season(self):
##        thorpy.get_application().fill((0,0,0))
##        pygame.display.flip()
        self.waiting = False
        self.season_idx += 1
        self.season_idx %= len(self.seasons)
        idx = self.season_idx
        self.set_season(idx)
        s = self.seasons[idx]
        thorpy.launch_blocking_alert(s.name+" has come.")
        self.storm_duration = -1
        self.reac_time_low()


    def refresh_temperature(self):
        #climate contribution
        xclim, yclim = self.get_clim_coord()
        clim_temp = self.climate.temp[xclim,yclim]
        clim_term = parameters.CLIMATE_FACTOR*clim_temp
        #altitude contribution
        height_temp = max(self.height, parameters.SUMMER_LEVEL)
        height_term = height_temp * parameters.TGRAD + parameters.ALT_0
        #
        season_term = self.seasons[self.season_idx].temp_shift
        self.temp = parameters.TEMP_0 + clim_term + height_term + season_term
        if self.is_winter:
            if self.temp > parameters.MIN_WINTER_TEMP:
                self.temp = parameters.MIN_WINTER_TEMP
        self.temp_text = int(self.temp)

    def near_chunks(self):
        """Iterate over chunks that are comprised within circle of given radius.
        Format of output chunks : cam format."""
        radius = parameters.RADIUS_LOAD
        cx, cy = self.cam.chunk
        for x in range(-radius,radius):
            for y in range(-radius,radius):
                if math.hypot(x,y) <= radius: #rel format
                    chunk = (self.cam.chunk + np.array((x,y)))%self.cam.world_size
                    yield chunk

    def old_chunks(self):
        """Return list cam chunks that are not comprised within circle of given
        radius. Format of output chunks : cam format."""
        old = []
        w,h = self.cam.world_size
        w2 = w//2
        h2 = h//2
        for chunk in self.cam.saved_chunks: #cam format
            dx,dy = np.abs(self.cam.chunk - chunk) #rel format
            if dx > w2:
                dx = w - dx
            if dy > h2:
                dy = h - dy
            if  math.hypot(dx,dy) > parameters.RADIUS_FREE:
                old.append(chunk)
        return old

    def load_chunks(self):
        e = gui.LifeBar("Generating chunks", color=(0,0,255), size=(300,50))
        e.center()
        e.set_life(0)
        #
        #step 1: erase old chunks
        for chunk in self.old_chunks():
            self.cam.saved_chunks.pop(chunk)
        #step 2: load new chunks
        i = 0.
        for chunk in self.near_chunks():
            e.set_life(i/parameters.MAX_CHUNKS)
            e.blit()
            e.update()
            i += 1.
            self.cam.get_surface(chunk)

    def get_distance_from_0(self):
        dx,dy = self.campos%parameters.WORLD_SIZE_PIX
        if dx > parameters.MAX_DIST[0]:
            dx = parameters.WORLD_SIZE_PIX[0] - dx
        if dy > parameters.MAX_DIST[1]:
            dy = parameters.WORLD_SIZE_PIX[1] - dy
        return math.sqrt(dx*dx + dy*dy)

    def reac_time(self):
        if parameters.BISURFACE:
            self.cam.iter_clouds()
        self.process_direction()
        if self.building_map:
            if parameters.USE_LOADER:
                print("Number of chunks in memory =", len(self.cam.saved_chunks))
                self.load_chunks()
##            else:
##                self.monitor.launch_fading_alert("Generating chunk...")
            self.building_map = False
        if self.i % parameters.MOD_LOW == 0:
            self.reac_time_low()
        if self.i % parameters.MOD_LIFE == 0:
            self.refresh_life_and_food()
##        if self.i % parameters.MOD_SAVE_GAME == 0:
##            self.monitor.launch_fading_alert("Saving game...")
##            self.save_game()
        #get wind properties
        self.wind.refresh()
        wx, wy = self.wind.windx, self.wind.windy
        if self.storm:
            self.storm.refresh()
            wx += self.storm.windx
            wy += self.storm.windy
        angle = math.atan2(wy,wx)
        vec_wind = Vector2(wx,wy)
        self.current_wind_draw = vec_wind * parameters.GIROUETTE_LENGTH
        if self.current_wind_draw.length() > parameters.GIROUETTE_LENGTH:
            self.current_wind_draw.scale_to_length(parameters.GIROUETTE_LENGTH)
        #get input direction
        if self.direction:
            input_direction = self.input_direction
        else:
            input_direction = Vector2()
        #get collisions
        collisions = self.cam.show(self.screen)
        self.height = collisions[0]
        self.collision_factor = self.controlled.compute_collision_factor(collisions, parameters.WATER_LEVEL)
        self.collision_factor_summer = self.controlled.compute_collision_factor(collisions, parameters.SUMMER_LEVEL)
        #refresh ship force and velocity
        if self.aboard:
            if self.collision_factor > 0:
                windforce = vec_wind*0.
            else:
                windforce = parameters.WIND_FACTOR*vec_wind
            self.ship.refresh(windforce,
                              parameters.DIR_FACTOR*input_direction) #DEBUG (*10)
##            self.ship.refresh(windforce,
##                              parameters.DIR_FACTOR*input_direction*10) #DEBUG (*10)
            self.ship.velocity -= (self.ship.velocity*self.collision_factor)
            life_cost = self.collision_factor * self.ship.velocity.length() * (2. - self.c.ship_skill) * (1.1-self.ship.weakness)
##            print(life_cost, self.c.ship_skill, self.ship.weakness)
            if life_cost > 0:
                self.ship.life -= life_cost * parameters.COLLISION_FACTOR
                self.ship.control_life()
                self.refresh_ship_life = True
            else:
                self.refresh_ship_life = False
        else: # .. or human
            vnorm = parameters.WALKING_SPEED * (1.-self.collision_factor)
            v = input_direction * vnorm
            self.controlled.velocity = v
            if self.collision_factor > 0.7:
                self.swimming = True
                self.controlled.velocity += parameters.WIND_FACTOR_SWIM*vec_wind
            else:
                self.swimming = False
            if v.length() > 0:
                target = self.controlled
                for c in self.living_chars:
                    if c is not target:
                        c.set_velocity_to_destination(self.cam, target.last_pos,
                                                        self.controlled.velocity.length())
                        c.img_pos += c.velocity - v
                        target = c
        #
        self.campos += self.controlled.velocity
        self.cam.pos = np.array(self.campos,dtype=int)
        if self.storm:
            self.falls.refresh()
            self.falls.blit()
        #
        self.blit_things()
        pygame.display.flip()
        self.refresh_img_pos()
        self.direction = False
        self.i += 1
        #

    def refresh_img_pos(self, delta=None):
##        for s in self.statics: #A faire dans l'ideal
##            s.refresh_img_pos(self, delta)
        for v in self.villages:
            v.refresh_img_pos(self, delta)
        if self.is_winter:
            for o in self.oasises:
                o.refresh_img_pos(self, delta)
##        for f in self.firs:
##            f.refresh_img_pos(self, delta)
        for f in self.flags:
            f.refresh_img_pos(self, delta)
        for t in self.treasures:
            t.refresh_img_pos(self, delta)
        if not self.aboard:
            self.ship.refresh_img_pos(self, delta)
        perigeo.refresh_img_pos(self, delta)

    def blit_villages(self):
        for v in self.villages: #blit houses
            v.blit(self.screen)
            if distance_to_center(v.pos+v.semisize) < v.maxwidth:
                if v.type == "f":
                    self.near_forest = v
                else:
                    self.near_village = v
                    if v.type == "c" :
                        self.near_camp = v

##    def blit_oasises(self):
##        for v in self.oasises: #blit houses
##            v.blit(self.screen)
##            if distance_to_center(v.pos+v.semisize) < v.maxwidth:
##                self.near_village = v

    def storm(self, value):
        if value:
            self.ship.imgs = self.ship.storm_imgs
        else:
            self.ship.imgs = self.ship.normal_imgs

    def blit_things(self):
        self.near_village = None
        self.near_camp = None
        self.near_forest = None
        self.blit_villages()
        if self.aboard or self.swimming:
            if self.aboard:
                self.ship.refresh_img(self.i, self.side)
                self.ship.smokegen.kill_old_elements()
                if self.i%10 == 0:
                    q = Vector2(parameters.CENTER)-self.input_direction*10
                    if self.side == SIDE_LEFT or self.side == SIDE_RIGHT:
                        q += (0,10)
                    self.ship.smokegen.generate(q)
            elif self.swimming:
                if self.i%20 == 0:
                    for c in self.living_chars:
                        self.ship.smokegen.generate(Vector2(c.img_pos))
            self.ship.smokegen.update_physics(-self.ship.velocity)
            self.ship.smokegen.draw(self.screen)
        self.screen.blit(perigeo.img, perigeo.img_pos)
        self.ship.blit(self.screen)
        if not self.aboard:
            for c in self.living_chars: #blit characters
                c.blit(self.screen)
        self.near_flag = self.get_near_flag()
        self.near_treasure = self.get_near_treasure()
        self.can_flag = False
        if len(self.flags) < parameters.MAX_FLAGS:
            if not self.aboard:
                if self.height > parameters.SUMMER_LEVEL:
                    self.can_flag = True
        for f in self.flags:
            f.blit(self.screen)
        for t in self.treasures:
            t.blit(self.screen)
        self.screen.blit(compass,compass_pos) #blit compass
        #blit thermo
        pos = fluid_pos[0], fluid_pos[1] + 44 - self.temp_pix
        pygame.draw.rect(self.screen, (255,0,0),
                         pygame.Rect(pos,(5,self.temp_pix)))
        self.screen.blit(thermo,thermo_pos)
        #gui
        self.monitor.blit()
        self.e_clock.blit()
        self.e_temp.blit()
        self.e_coords.blit()
        self.e_life.blit()
        pos_life = self.e_life.get_fus_rect()
        img_arrow = imgs_arrows[self.n_hunt]
        pos_arrows = img_arrow.get_rect()
        pos_arrows.center = pos_life.center
        pos_arrows.top = pos_life.bottom + 10
        self.screen.blit(img_arrow, pos_arrows)
        pygame.draw.line(self.screen, parameters.GIROUETTE_COLOR,
                            girouette_pos, self.current_wind_draw+girouette_pos,
                            3)
##        pygame.draw.rect(self.screen,(255,0,0),pygame.Rect(parameters.CENTER[0],parameters.CENTER[1],4,4))


    def try_building_village(self, chunk, hmap):
        return try_building_structure(self, chunk, (houses[0],houses[1]), hmap, "v")

    def try_building_oasis(self, chunk, hmap):
        return try_building_structure(self, chunk, (oasises[0],oasises[1]), hmap, "o")

    def try_building_firs(self, chunk, hmap):
        return try_building_structure(self, chunk, (firs[0],firs[1]), hmap, "f")

    def try_putting_treasure(self, chunk, hmap):
        if self.save:
            if chunk in self.save.treasures_taken:
                return False
        if not(chunk in self.treasures_put):
            np.random.seed(chunk)
            if np.random.random() < parameters.TREASURE_PROB:
                i = 0
                while i < parameters.VILLAGE_TRY:
                    chunkpos = np.random.randint(0,parameters.S,2)
                    cx,cy = chunkpos
                    if hmap[cx,cy] > parameters.VILLAGE_LEVEL:
                        absolute_pos = np.array(chunk)*parameters.S + chunkpos
                        relative_pos = self.get_relative_position(absolute_pos)
                        food = np.random.randint(0, 100)
                        nhunt = np.random.randint(1, 5)
                        t = Treasure(treasure, relative_pos, food, nhunt, chunk)
                        self.treasures.append(t)
                        self.treasures_put.append(chunk)
                        print("Treasure added", chunk)
                        return True
                    i += 1
        return False


    def add_peak(self, chunk, gaussian):
        if chunk in self.peaks:
            self.peaks[chunk].append(gaussian)
        else:
            self.peaks[chunk] = [gaussian]

##    def save_game(self):
##        f = open(parameters.FILE_SAVE, "w")
##        f.write(str(self.campos))
##        f.close()
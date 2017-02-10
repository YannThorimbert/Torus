import pygame
from pygame.math import Vector2
import parameters
from controllable import Controllable
import fx

def rotate_in_water(img, degrees):
    i = pygame.transform.rotate(img, degrees)
    ws,hs = img.get_size()
    wi,hi = i.get_size()
    s = pygame.Surface((ws,hs))
    s.fill((255,255,255))
    s.blit(i,((ws-wi)//2,0))
    s.set_colorkey((255,255,255))
    return s

def get_n_phases(img, degree, n=parameters.N_PHASES_SHIP):
    imgs = []
    for i in range(1,n):#n-1
        angle = i*degree/n
        imgs.append(rotate_in_water(img,angle))
    imgs += imgs[::-1]#n-1
    imgs2 = []
    for i in range(1,n):#n-1
        angle = i*degree/n
        imgs2.append(rotate_in_water(img,-angle))
    imgs2 += imgs2[::-1]#n-1
    return imgs + imgs2

class Ship(Controllable):

    def __init__(self, mass, maxvel, life, captain):
        Controllable.__init__(self)
        self.model = 0
        self.max_food = 2*parameters.MAX_WSF
        self.food = self.max_food
        self.mass = mass
        self.maxvel = maxvel/10.
        self.life = life
        self.force = Vector2()
        self.img = None
        self.captain = captain
        self.name = "Ship"
        self.dead = False
        self.weakness = 0.
        self.imgs = None
##        self.reflects = None
        self.normal_imgs = None
        self.storm_imgs = None
        self.i = 0
        self.mod_rot = parameters.MOD_LOW
        self.mod_phase = parameters.MOD_PHASE_SHIP
        self.side = 0
        self.smokegen = fx.get_smokegen(n=100, color=(255,255,255), grow=0.1,
                                            i=30, prob=0.1, alpha0=255)

    def refood_from(self, stock):
        lack = self.max_food - self.food
        qty = min(lack, stock.food)
        self.food += qty
        stock.food -= qty

    def refresh(self, wind, input_direction):
        if self.life > 0:
            speeding = input_direction*self.maxvel
        else:
            speeding = Vector2()
        friction = self.velocity*parameters.FRICTION_FACTOR
        self.force = wind + self.captain.ship_skill*(speeding-friction)*parameters.SHIP_SPEED_FACTOR
        a = self.force / self.mass
        self.velocity += a * parameters.DT
##        self.smokegen.kill_old_elements()

    def compute_collision_factor(self, collisions, level):
        factor = 0.
        for h in collisions:
            if h > level:
                factor += 1.
        return factor / parameters._NCOLL

    def build_imgs(self, degree, lrfr, storm=False):
        imgs = []
        for img in lrfr:
            imgs += get_n_phases(img, degree)
        return imgs

    def refresh_img(self, i, side):
        self.side = side
##        print(side, self.i, side+self.i, len(self.imgs))
        self.img = self.imgs[side+self.i]
##        self.reflect = self.reflects[side+self.i]
        if i%self.mod_rot == 0:
            self.i = (self.i+1)%self.mod_phase

    def anchor(self):
        self.img = self.imgs[self.side]
##        self.reflect = self.reflects[self.side]

    def make_consistent(self):
        if self.food > self.max_food: self.food = self.max_food
        if self.food < 0: self.food = 0

    def add_food(self, qty):
        self.food += qty
        self.make_consistent()

    def autoset_captain(self, game):
        best = -1
        cap = None
        for c in game.living_chars:
            if c.ship_skill > best:
                best = c.ship_skill
                cap = c
        assert cap is not None
        self.captain = cap

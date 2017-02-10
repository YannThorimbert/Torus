from __future__ import print_function, division
import pygame, time
import numpy as np
from pygame import gfxdraw
from numpy.polynomial.polynomial import polyval2d
import pygame.surfarray
import fx
from pygame.math import Vector2

import thorpy
import parameters

################################################################################
SEED = None
WORLD_SIZE = None
COLORSCALE = None

APPROX_SCREEN_W = 700 #the actual screen width will be lower or equal
DEGREE = 4 #degree of the polynom + 1
LEVEL_ITERATIONS = 1
DEEP_CONSTANT = 1 #max_n/2**depth = constant #change le "zoom". Bonne valeur = 4
DEPTH = 6 #4 commence a etre detaille
MAX_N = DEEP_CONSTANT*2**DEPTH
LEVELS = range(DEPTH)
Kh = 1.
Dn, Dh = 2, 2.
En, Eh = 1., 1.

################################################################################

PARAM_N, PARAM_H = [], []

assert isinstance(Dn, int) and En >= 1.
for i in LEVELS:
    PARAM_N.append(int(MAX_N//Dn**(En*i)))
    PARAM_H.append(Kh*Dh**(Eh*i))
PARAM_N = PARAM_N[::-1]
PARAM_H = PARAM_H[::-1]

#sum of param_h*LI = 0.5, so hmap goes from -0.5 to 0.5
##mieux: get_seed genere direct dans range 0,1, et ensuite sum of param = 1. et pas de normalize
maxh = sum(PARAM_H)*LEVEL_ITERATIONS
for i in LEVELS:
    PARAM_H[i] /= (2.*maxh)


print("N:", PARAM_N)

S = (APPROX_SCREEN_W // MAX_N) * MAX_N

for n in PARAM_N:
    if S%n != 0:
        print("problem n", S,n,S%n)
        break

RES, DOMAIN = [], []
for k in LEVELS:
    n = PARAM_N[k]
    RES.append(int(S / n))
    DOMAIN.append(np.arange(0., 1., 1./RES[k]))

def get_x(k):
    dom = DOMAIN[k]
    res = RES[k]
    a = np.zeros((res,res))
    for x in range(res):
        a[x,:] = dom[x]
    return a


K2, K3 = 3., -2.

print("Preparing cache...")
CACHE_SPACE = {}
DCACHE_SPACE = {}
##XY_SPACE = None
XSPACE = None
YSPACE = None

def cache():
    global CACHE_SPACE, DCACHE_SPACE, XSPACE, YSPACE
    XSPACE = np.zeros((S,S))
    for x in range(S):
        XSPACE[x,:] = x
    YSPACE = XSPACE.T
##    XY_SPACE = np.outer(xarange,xarange)
    for k in LEVELS:
        print("-", end="")
        x = get_x(k)
        x2 = x*x
        x3 = x2*x
        y = x.T
        y2 = x2.T
        y3 = x3.T
        CACHE_SPACE[k,0] = K3*x3 + K2*x2
        CACHE_SPACE[k,1] = K3*y3 + K2*y2
        xy = x*y
        x2y = x*xy
        xy2 = y*xy
        x3y = x*x2y
        CACHE_SPACE[(k,2)] = xy - K2*(x2y + xy2) - K3*(x3y + x3y.T)
        #dx
        DCACHE_SPACE[k,0] = 3*K3*x2 + 2*K2*x
        DCACHE_SPACE[k,1] = y - K2*(2*xy+y2) - K3*(3*x2y+y3)
        #dy
        DCACHE_SPACE[k,2] = 3*K3*y2 + 2*K2*y
        DCACHE_SPACE[k,3] = x - K2*(2*xy+x2) - K3*(3*xy2+x3)
    print("> cache finished")


def RandArray(c, n):
    return c*(2*np.random.random((n,n)) - 1)

def set_seeded_condition(l, t, a, n, i, val, flag): #rajouter SEED
    #lines (can be optimized, corners don't need to be set here)
    right = (l+1)%WORLD_SIZE[0]
    bottom = (t+1)%WORLD_SIZE[1]
    np.random.seed((l,t,n,i,flag,0)) #left
    a[0,:] = val*(2*np.random.random(n+1) - 1)
    np.random.seed((right,t,n,i,flag,0)) #right
    a[n,:] = val*(2*np.random.random(n+1) - 1)
    np.random.seed((l,t,n,i,flag,1)) #top
    a[:,0] = val*(2*np.random.random(n+1) - 1)
    np.random.seed((l,bottom,n,i,flag,1)) #bottom
    a[:,n] = val*(2*np.random.random(n+1) - 1)
    #corners
    np.random.seed((l,t,n,i,flag)) #topleft
    a[0,0] = val*(2*np.random.random() - 1)
    np.random.seed((right,t,n,i,flag)) #topright
    a[n,0] = val*(2*np.random.random() - 1)
    np.random.seed((l,bottom,n,i,flag)) #bottomleft
    a[0,n] = val*(2*np.random.random() - 1)
    np.random.seed((right,bottom,n,i,flag)) #bottomright
    a[n,n] = val*(2*np.random.random() - 1)


def get_seeded_conditions(truechunk, k, i):
    n = PARAM_N[k]
    h = PARAM_H[k]
    l,t = truechunk
    np.random.seed([l,t,n,i,0+SEED]) #bulk
    tabh = RandArray(h,n+1)
    set_seeded_condition(l,t,tabh,n,i,h,1+SEED) #boundaries
    return tabh



class Camera:

    def __init__(self, chunk, pos, seed, world_size):
        global SEED, WORLD_SIZE
        SEED = seed
        self.seed = seed
        WORLD_SIZE = world_size
        self.colorscale = None
        self.seed = seed
        self.world_size = world_size
        self.world_largest_size = np.max(world_size)
        self.chunk = np.array(chunk)
        self.pos = np.array(pos) + self.chunk*S
        self.saved_chunks = {}
        self.game = None
        self.villages = []

    def reset(self,seed):
        global SEED, WORLD_SIZE
        SEED = seed
        self.seed = seed
        WORLD_SIZE = parameters.WORLD_SIZE
        self.world_size = parameters.WORLD_SIZE
        self.world_largest_size = np.max(WORLD_SIZE)
        self.saved_chunks = {}
        self.villages = []
        #
        assert not self.game.treasures
        self.game.treasures = []
        self.game.treasures_put = []
        self.game.villages = []
        self.game.oasies = []


    def set_colorscale(self, colorscale):
        global COLORSCALE
        COLORSCALE = colorscale
        self.colorscale = colorscale


    def gen(self, hmap, chunk, k, i): #generate world at level k
        n = PARAM_N[k]
        tabh = get_seeded_conditions(chunk, k, i)
##        print("level =",k,", n =",n, ", x0 =", (PARAM_N[k]-n), ", seedshape =",tabh.shape)
        for x in range(n):
            for y in range(n):
                p = Polynom(tabh[x:x+2,y:y+2])
                p.fill_array(hmap, k, x, y)

    def gen_d(self, dmap, d, chunk, k, i): #generate world at level k
        n = PARAM_N[k]
        tabh = get_seeded_conditions(chunk, k, i)
        for x in range(n):
            for y in range(n):
                p = Polynom(tabh[x:x+2,y:y+2])
                p.fill_array_d(dmap, d, k, x, y)

    def compute_hmap(self, chunk):
        hmap = np.zeros((S,S))
        for k in LEVELS:
            for li in range(LEVEL_ITERATIONS):
                self.gen(hmap, chunk, k, li)
##        if self.game:
##            gaussians = self.game.peaks.get(tuple(chunk))
##            if gaussians:
##                for gaussian in gaussians:
##                    gaussian.add_to(hmap)
        hmap = normalize_hmap(hmap)
        return hmap

    def compute_nonnormalized_dmap(self, chunk, d):
        dmap = np.zeros((S,S))
        for k in LEVELS:
            for li in range(LEVEL_ITERATIONS):
                self.gen_d(dmap, d, chunk, k, li)
        return dmap

    def get_surface(self, truechunk):
        truechunk %= WORLD_SIZE
        chunk = tuple(truechunk)
        couple = self.saved_chunks.get(chunk, [None,None])
        if couple[0] is None: #then build both hmap and surface
            hmap = self.compute_hmap(truechunk)
            couple[0] = hmap
            self.saved_chunks[chunk] = couple
            if self.game is not None:
                if not chunk in self.villages:
                    self.game.try_building_village(chunk, hmap)
                    self.game.try_building_oasis(chunk, hmap)
                    self.game.try_putting_treasure(chunk, hmap)
                    self.game.try_building_firs(chunk,hmap)
                    self.villages.append(chunk)
                self.game.building_map = True
        if couple[1] is None: #then build surface only
            cmap = COLORSCALE.get(couple[0])
            surf = pygame.surfarray.make_surface(cmap)
##            surf.convert() #should i or should i not ?
            couple[1] = surf
        return couple[1]

    def show(self, screen):
        self.chunk = self.pos//S
        relpos = self.pos%S
##        print(self.chunk, self.chunk%WORLD_SIZE)
        tl = self.get_surface(self.chunk)
        tr = self.get_surface(self.chunk+(1,0))
        bl = self.get_surface(self.chunk+(0,1))
        br = self.get_surface(self.chunk+(1,1))
        postl = -relpos
        postr = postl + (S,0)
        posbl = postl + (0,S)
        posbr = postl + (S,S)
        screen.blit(tl,postl)
        screen.blit(tr,postr)
        screen.blit(bl,posbl)
        screen.blit(br,posbr)
        if parameters.SHOW_GRID:
            for p in [postl,postr,posbl,posbr]:
                pygame.draw.rect(screen, (200,200,200), pygame.Rect(p,(S,S)), 1)
        tlrect = pygame.Rect(-relpos, (S,S))
        trrect = pygame.Rect(postr, (S,S))
        blrect = pygame.Rect(posbl, (S,S))
        brrect = pygame.Rect(posbr, (S,S))
        points = [(0,0),(-10,0),(10,0)]
        rects = [(tlrect,self.chunk),(trrect,self.chunk+(1,0)),
                 (blrect,self.chunk+(0,1)),(brrect,self.chunk+(1,1))]
        collisions = []
        for x,y in parameters._COLLISION_POINTS:
##            pygame.draw.rect(screen,(0,0,0),pygame.Rect(x,y,2,2))
            for r,c in rects:
##                pygame.draw.rect(screen,(0,0,0),r)
                if r.collidepoint((x,y)):
                    chunk = tuple(c%WORLD_SIZE)
                    h = self.saved_chunks[chunk][0][x-r.x,y-r.y]
                    collisions.append(h)
        return collisions

class Cloud:

    def __init__(self,args):
        x,y,vx,vy = args
        self.x = x
        self.y = y
        self.vx = vx/2000.
        self.vy = vy/200000.
        self.i = self.x%3

    def iterate(self):
        self.x += self.vx
        self.y += self.vy
        if self.x < -192:
            self.x = S
        elif self.x > S:
            self.x = -192
        if self.y < -49:
            self.y = S
        elif self.y > S:
            self.y = -49

class CameraBisurface(Camera):

    def __init__(self, chunk, pos, seed, world_size):
        Camera.__init__(self, chunk, pos, seed, world_size)
        self.clouds = []
        self.init_clouds()
        self.ship = None
        self.shiph = None

    def init_clouds(self):
        np.random.seed()
        self.clouds = []
        for i in range(parameters.NCLOUDS):
            self.clouds.append(Cloud(np.random.randint(0,S,4)))

    def iter_clouds(self):
        for cloud in self.clouds:
            cloud.iterate()
            cloud.x -= self.game.controlled.velocity[0]/10.
            cloud.y -= self.game.controlled.velocity[1]/10.
        if parameters.REFLECT:
            self.iter_ship()

    def iter_ship(self):
        self.ship = pygame.transform.flip(self.game.ship.img,False,True)
        self.ship.set_alpha(50)
        self.shiph = self.ship.get_height()

    def get_surface(self, truechunk):
        truechunk %= WORLD_SIZE
        chunk = tuple(truechunk)
        couple = self.saved_chunks.get(chunk, [None,None])
        if couple[0] is None: #then build both hmap and surface
            hmap = self.compute_hmap(truechunk)
            couple[0] = hmap
            self.saved_chunks[chunk] = couple
            if self.game is not None:
                if not chunk in self.villages:
                    self.game.try_building_village(chunk, hmap)
                    self.game.try_building_oasis(chunk, hmap)
                    self.game.try_putting_treasure(chunk, hmap)
                    self.game.try_building_firs(chunk,hmap)
                    self.villages.append(chunk)
                self.game.building_map = True
        if couple[1] is None: #then build surface only
            hmap = couple[0]
            cmap = COLORSCALE.get(couple[0])
            cmap_land, cmap_sea = np.zeros((S,S,3),dtype=int), np.zeros((S,S,3),dtype=int)
            above = hmap>parameters.WATER_LEVEL
            below = np.logical_not(above)
            cmap_land[above] = cmap[above]
            cmap_sea[below] = cmap[below]
            land = pygame.surfarray.make_surface(cmap_land).convert_alpha()
            sea = pygame.surfarray.make_surface(cmap_sea).convert_alpha()
            #
##            aland = pygame.surfarray.pixels_alpha(land)
##            asea = pygame.surfarray.pixels_alpha(sea)
            #
            pygame.surfarray.pixels_alpha(land)[below] = 0.
            pygame.surfarray.pixels_alpha(sea)[above] = 0.

##            surf.convert() #should i or should i not ?
            couple[1] = (land, sea)
        return couple[1]

    def show(self, screen):
        self.chunk = self.pos//S
        relpos = self.pos%S
##        print(self.chunk, self.chunk%WORLD_SIZE)
        tl_land, tl_sea = self.get_surface(self.chunk)
        tr_land, tr_sea = self.get_surface(self.chunk+(1,0))
        bl_land, bl_sea = self.get_surface(self.chunk+(0,1))
        br_land, br_sea = self.get_surface(self.chunk+(1,1))
        postl = -relpos
        postr = postl + (S,0)
        posbl = postl + (0,S)
        posbr = postl + (S,S)
        #
        screen.blit(tl_sea,postl)
        screen.blit(tr_sea,postr)
        screen.blit(bl_sea,posbl)
        screen.blit(br_sea,posbr)
        #
        for cloud in self.clouds:
            screen.blit(self.game.clouds[cloud.i], (cloud.x,cloud.y))
        if parameters.REFLECT:
            if self.ship and not self.game.storm:
                screen.blit(self.ship, self.game.ship.img_pos+(0,self.shiph))
        if parameters.RAIN_IMPACTS:
            if self.game.storm and not(self.game.is_winter):
                rain = self.game.falls
##                fx.smokegen.kill_old_elements() #....
                fx.smokegen.natural_kill()
                k = self.game.i%parameters.RAIN_DISTRIBUTIONS
                for i in range(parameters.RAIN_IMPACTS):
                    coord = rain.impactsx[k][i], rain.impactsy[k][i]
                    fx.smokegen.generate(Vector2(coord))
                fx.smokegen.update_physics(-self.game.controlled.velocity)
                fx.smokegen.draw(screen)
        #
        screen.blit(tl_land,postl)
        screen.blit(tr_land,postr)
        screen.blit(bl_land,posbl)
        screen.blit(br_land,posbr)
        #
        if parameters.SHOW_GRID:
            for p in [postl,postr,posbl,posbr]:
                pygame.draw.rect(screen, (200,200,200), pygame.Rect(p,(S,S)), 1)
        tlrect = pygame.Rect(-relpos, (S,S))
        trrect = pygame.Rect(postr, (S,S))
        blrect = pygame.Rect(posbl, (S,S))
        brrect = pygame.Rect(posbr, (S,S))
        points = [(0,0),(-10,0),(10,0)]
        rects = [(tlrect,self.chunk),(trrect,self.chunk+(1,0)),
                 (blrect,self.chunk+(0,1)),(brrect,self.chunk+(1,1))]
        collisions = []
        for x,y in parameters._COLLISION_POINTS:
##            pygame.draw.rect(screen,(0,0,0),pygame.Rect(x,y,2,2))
            for r,c in rects:
##                pygame.draw.rect(screen,(0,0,0),r)
                if r.collidepoint((x,y)):
                    chunk = tuple(c%WORLD_SIZE)
                    h = self.saved_chunks[chunk][0][x-r.x,y-r.y]
                    collisions.append(h)
        return collisions


class Climate:

    def __init__(self, seed):
        self.cam = Camera(chunk=(0,0), pos=(0,0), seed=seed, world_size=(1,1))
        self.temp = self.cam.compute_hmap((0,0))


class Polynom:

    def __init__(self, h):
        self.dhx = h[1,0]-h[0,0]
        self.dhy = h[0,1]-h[0,0]
        self.A = self.dhx-h[1,1]+h[0,1]
        self.h0 = h[0,0]

    def point_eval(self,x,y):
        result = self.dhx*(K3*x*x*x + K2*x*x) +\
                 self.dhy*(K3*y*y*y + K2*y*y) +\
                 self.A*(x*y - K2*(x*x*y + x*y*y) - K3*(x*x*x*y + x*y*y*y)) +\
                 self.h0
        return result

    def domain_eval(self, k):
        result = self.dhx*CACHE_SPACE[k,0] +\
                 self.dhy*CACHE_SPACE[k,1] +\
                 self.A*CACHE_SPACE[k,2] +\
                 self.h0
        return result

    def fill_array(self, a, k, x0, y0):
        res = RES[k]
        x0 *= res
        y0 *= res
        a[x0:x0+res,y0:y0+res] += self.domain_eval(k)

    def domain_eval_f(self, k):
        result = self.dhx*DCACHE_SPACE[k,0] +\
                 self.A*DCACHE_SPACE[k,1]
        return result

    def domain_eval_g(self, k):
        result = self.dhy*DCACHE_SPACE[k,2] +\
                 self.A*DCACHE_SPACE[k,3]
        return result

    def fill_array_d(self, a, d, k, x0, y0):
        res = RES[k]
        x0 *= res
        y0 *= res
        if d == 0: #absolutely not optimal. just for demo.
            func = self.domain_eval_f
        else:
            func = self.domain_eval_g
        a[x0:x0+res,y0:y0+res] += func(k)


class Gaussian:

    def __init__(self, x, y, a, sigx, sigy):
        self.x, self.y = x, y
        self.a = a
        self.sx2, self.sy2 = sigx*sigx, sigy*sigy

    def add_to(self, hmap):
        dx = XSPACE-self.x
        dy = YSPACE-self.y
        hmap += self.a*np.exp(-dx*dx/(2.*self.sx2) -dy*dy/(2.*self.sy2))



def normalize_hmap(hmap):
        return hmap + 0.5




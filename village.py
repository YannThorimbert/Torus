import numpy as np
from pygame.math import Vector2
import parameters
from controllable import FoodStock, Tile

def force_build_structure(game, imgs, chunk, chunkpos, n, type_):
    """Actual village builder"""
    id_ = chunk
    if type_ == "c":
        relative_pos = np.array(parameters.CENTER)
        camp = Camp(imgs, relative_pos, n, id_)
        game.villages.append(camp)
    elif type_ == "o":
        absolute_pos = np.array(chunk)*parameters.S + chunkpos
        relative_pos = game.get_relative_position(absolute_pos)
        print("oasis added to ", chunk)
        oasis = Oasis(imgs, relative_pos, n, id_)
        game.oasises.append(oasis)
        if not game.is_winter:
            game.villages.append(oasis)
    elif type_ == "f":
        absolute_pos = np.array(chunk)*parameters.S + chunkpos
        relative_pos = game.get_relative_position(absolute_pos)
        print("forest added to ", chunk)
        forest = Forest(imgs, relative_pos, n, id_)
        game.villages.append(forest)
    else:
        absolute_pos = np.array(chunk)*parameters.S + chunkpos
        relative_pos = game.get_relative_position(absolute_pos)
        print("village added to ", chunk)
        game.villages.append(Village(imgs, relative_pos, n, id_))
##    print("generating village", chunk, n, relative_pos)



def look_for_biggest_structure(game, chunk, imgs, hmap, nmax, type_):
    """Build village of maximum size (can be 0)"""
    for n in range(nmax,0,-1):
        i = 0
        m = parameters.MAX_VILLAGE_WIDTH * n / parameters.MAX_VILLAGE_SIZE
        while i < parameters.VILLAGE_TRY:
            chunkpos = np.random.randint(0,parameters.S,2)
            cx,cy = chunkpos
            h = np.sum(hmap[cx:cx+m,cy:cy+m]) / (m*m)
            if h > parameters.VILLAGE_LEVEL:
                force_build_structure(game, imgs, chunk, chunkpos, n, type_)
                return n
            i += 1
    return 0


def look_for_structure(game, chunk, imgs, hmap, n, type_):
    """If possible, build village"""
    i = 0
    m = parameters.MAX_VILLAGE_WIDTH * n / parameters.MAX_VILLAGE_SIZE
    while i < parameters.VILLAGE_TRY:
        chunkpos = np.random.randint(0,parameters.S,2)
        cx,cy = chunkpos
        h = np.sum(hmap[cx:cx+m,cy:cy+m]) / (m*m)
        if h > parameters.VILLAGE_LEVEL:
            force_build_structure(game, imgs, chunk, chunkpos, n, type_)
            return True
        i += 1
    return False


def try_building_structure(game, chunk, imgs, hmap, type_):
    """Probabilistic village builder"""
    chunkx, chunky = chunk
##    probability_x = 1. - chunkx/(game.cam.world_size[0]*parameters.MAX_VILLAGE_DIST)
##    probability_y = 1. - chunky/(game.cam.world_size[1]*parameters.MAX_VILLAGE_DIST)
    #prob linearly decreases with distance
    chunk_dist = chunkx*chunkx+chunky*chunky
##    dc = 0
    if type_ == "o":
        probability = parameters.OASIS_PROB
        dc = 1
    elif type_ == "f":
        probability = parameters.FOREST_PROB
        dc = 3
    else:
        probability = 1. - chunk_dist/game.cam.world_largest_size*parameters.MAX_VILLAGE_DIST
        probability *= parameters.VILLAGE_MAX_PROBABILITY
        dc = 2
    print("probability, chunk", probability, chunk,dc,type_)
    np.random.seed((chunk[0]+dc,chunk[1]))
    if np.random.random() < probability:
        n = np.random.randint(1, parameters.MAX_VILLAGE_SIZE)
        return look_for_structure(game, chunk, imgs, hmap, n, type_)
    return False


def get_distribution(n):
    w = int(np.sqrt(n)*parameters.VILLAGE_SPACING)
    if w*w < n:
        w += 1
    r = w*w/(n*n)
    is_house = np.random.random((w,w)) < r
    s = np.sum(is_house)
    if s > n:
        while s > n:
            x,y = np.random.randint(0,w,2)
            is_house[x,y] = False
            s = np.sum(is_house)
    elif s < n:
        while s < n:
            x,y = np.random.randint(0,w,2)
            is_house[x,y] = True
            s = np.sum(is_house)
    house_type = np.random.random((w,w)) < 0.5
    return is_house, house_type.astype(int)


class Village(FoodStock):

    def __init__(self, imgs, pos, n, id_):
        FoodStock.__init__(self,n)
        self.max_food = int(parameters.MAX_VSF*n)
        self.food = self.max_food
        self.houses = []
        self.pos = pos
        occupied, type_ = get_distribution(n)
        for x in range(occupied.shape[0]):
            xpos = x*parameters.HOUSE_SPACING
            for y in range(occupied.shape[1]):
                if occupied[x,y]:
                    ypos =  y * parameters.HOUSE_SPACING
                    pos = np.array((xpos,ypos))
                    pos += np.random.randint(-parameters.HOUSE_RAND,
                                                parameters.HOUSE_RAND,2)
                    img = imgs[type_[x,y]]
                    self.houses.append(Tile(img, pos))
        self.semisize = Vector2(xpos+parameters.HOUSE_SPACING, ypos+parameters.HOUSE_SPACING)/2
        self.maxwidth = max(2*self.semisize)
        self.name = "Village"
        self.pos -= self.semisize
        self.type = "v"
        self.id = id_

    def blit(self, screen):
##        print(self.pos)
        for h in self.houses:
            screen.blit(h.img, h.img_pos + self.pos)

    def refresh_img_pos(self, game, delta=None):
        if delta is None: delta = game.controlled.velocity
        self.pos -= delta
        if abs(self.pos[0]) > parameters.S:
            self.pos[0] %= game.cam.world_size[0]*parameters.S
        if abs(self.pos[1]) > parameters.S:
            self.pos[1] %= game.cam.world_size[1]*parameters.S



class Camp(Village):

    def __init__(self, imgs, pos, n, id_):
        Village.__init__(self, imgs, pos, n, id_)
        self.food = 0
        self.name = "Camp"
        self.type = "c"


class Oasis(Village):
    def __init__(self, imgs, pos, n, id_):
        Village.__init__(self, imgs, pos, n, id_)
        self.food = int(parameters.MAX_OSF*n)
        self.name = "Oasis"
        self.type = "o"

class Forest(Village):
    def __init__(self, imgs, pos, n, id_):
        Village.__init__(self, imgs, pos, n, id_)
        self.food = int(parameters.MAX_OSF*n)
        self.name = "Forest"
        self.type = "f"


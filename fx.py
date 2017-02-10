import pygame, random, thorpy
import parameters
import numpy as np
from pygame.math import Vector2

class SmokeGenerator(object):
    current_id = 0

    def __init__(self, samples, n, opac=None, mov=1, grow=0.5, prob=0.2, i=2,
                    color=None, alpha0=255, size0=None, smoothscale=False,
                    copy=False):
        if not copy:
            samples = [s.copy() for s in samples]
        self.samples = samples
        self.n = n
        opac = alpha0/n if opac is None else opac
        self.opac = opac
        self.mov = mov
        self.grow = grow
        self.prob = prob
        self.alpha0 = alpha0
        if not copy:
            if smoothscale:
                self.scale_func = pygame.transform.smoothscale
            else:
                self.scale_func = pygame.transform.scale
            if isinstance(size0, tuple):
                self.size0 = {s:size0 for s in self.samples}
            elif size0 is None:
                self.size0 = {s:s.get_size() for s in self.samples}
            else:
                self.size0 = size0
            if color is not None:#for the moment colorkey is hardcoded to white, and color source to black
                color=(254,254,254) if color == (255,255,255) else color
                for s in self.samples:
                    thorpy.change_color_on_img_ip(  img=s,
                                                    color_source=(0,0,0),
                                                    color_target=color,
                                                    colorkey=(255,255,255))
            self.imgs = self.build_imgs() #on the form img[sample][time]
        self.i = i
        self.smokes = []
        self.body = None
        self.id = SmokeGenerator.current_id
        SmokeGenerator.current_id += 1

    def get_copy(self):
        gen = SmokeGenerator(samples=self.samples, n=self.n, mov=self.mov,
                                prob=self.prob, i=self.i, copy=True)
        gen.imgs = self.imgs
        return gen

    def build_imgs(self):
        imgs = {}
        for s in self.samples:
            imgs[s] = []
            w,h = self.size0[s]
            alpha = self.alpha0
            for i in range(self.n):
                w += self.grow
                h += self.grow
                alpha -= self.opac
                img = self.scale_func(s, (int(w), int(h)))
                img.set_colorkey((255,255,255))
                img.set_alpha(int(alpha))
                imgs[s].append(img)
        return imgs

    def generate(self, q):
        self.smokes.append(Smoke(q, self))

    def kill_old_elements(self):
##        for s in self.smokes:
##            parent.partial_blit(None, s.rect)
        if len(self.smokes) > self.n:
            self.smokes = self.smokes[1::]
##        delta = len(self.smokes) - self.n
##        if delta > 0:
##            self.smokes = self.smokes[delta::]

    def natural_kill(self):
        self.smokes = [s for s in self.smokes if not s.dead]

    def draw(self, surface):
        for s in self.smokes:
            if not s.dead:
                surface.blit(s.img, s.rect.topleft)

##    def draw(self, surface, parent):
##        if len(self.smokes) > self.n:
##            self.smokes = self.smokes[1::]
##        for s in self.smokes:
##            parent.partial_blit(None, s.rect)
##        for s in self.smokes:
##            if not s.dead:
##                surface.blit(s.img, s.rect.topleft)

    def update_physics(self, dq):
        for s in self.smokes:
            s.update_physics(dq)

    def add_to(self, body, position):
##        body.fight.smokes.append((self, body, position))
##        print("adding", self, body)
        self.body = body
        body.fight.smokes.insert(0, (self, body, position))


class Smoke(object):

    def __init__(self, q, generator):
        self.q = q
        self.t = 0
        self.s = random.choice(generator.samples)
        self.generator = generator
        self.img = self.generator.imgs[self.s][0]
        self.rect = self.img.get_rect()
        self.rect.center = self.q
        self.dead = False

    def update_physics(self, dq):
        if self.t < self.generator.n:
            self.img = self.generator.imgs[self.s][self.t]
            if random.random() < self.generator.prob:
                dx = random.randint(-self.generator.mov,self.generator.mov)
                dy = random.randint(-self.generator.mov,self.generator.mov)
                self.q += (dx, dy)
            self.q += dq
            self.rect = self.img.get_rect()
            self.rect.center = self.q
            self.t += 1
        else:
            self.dead = True



C_BIG = (255,0,0)

smokegen = None


def get_smokegen(n=15, color=(99,99,99), grow=0.4, i=2, prob=0.3, alpha0=255,
                    size0=None):
    smoke_image1 = thorpy.load_image("smoke.png", (255,255,255))
    smoke_image2 = thorpy.load_image("smoke2.png", (255,255,255))
    return SmokeGenerator([smoke_image1, smoke_image2],
                                 n=n,
                                 prob=prob,
                                 grow=grow,
                                 i=i,
                                 color=color,
                                 alpha0=alpha0,
                                 size0=size0)



def get_rain_img(w):
    img = pygame.Surface((w,w))
    img.fill((0,0,0))
    pygame.draw.aaline(img, (150,150,150), (w//2,0), (w//2,w))
    img.convert()
    img.set_colorkey((0,0,0))
    return img

def get_rain_imgs(w):
    img = get_rain_img(w)
    return get_imgs(img)

def get_imgs(img):
    imgs = []
    for i in range(-180,180):
        imgs.append(pygame.transform.rotate(img,i))
    return imgs

def set_rain_smokegen():
    global smokegen
    smokegen = get_smokegen(n=30, color=(255,255,255), grow=0.1, i=30, prob=0.1, alpha0=155)

class Rain:

    def __init__(self, game, n, img=None):
##        self.img = get_rain_img(20)
        self.img = None
        self.n = n
        self.dropsx = np.random.randint(0,parameters.S,n)
        self.dropsy = np.random.randint(0,parameters.S,n)
        self.impactsx = []
        self.impactsy = []
        for i in range(parameters.RAIN_DISTRIBUTIONS):
            self.impactsx.append(np.random.randint(0,parameters.S,parameters.RAIN_IMPACTS))
            self.impactsy.append(np.random.randint(0,parameters.S,parameters.RAIN_IMPACTS))
        self.impact = thorpy.load_image("smoke.png")
        self.game = game
        if img is None:
            self.imgs = get_rain_imgs(20)
        else:
            self.imgs = get_imgs(img)

    def refresh(self):
        self.dropsx += int(self.game.current_wind_draw[0]*(0.4*(1.+random.random())))
        self.dropsy += int(self.game.current_wind_draw[1]*(0.4*(1.+random.random())))
        self.dropsx %= parameters.S
        self.dropsy %= parameters.S
        angle = self.game.current_wind_draw.angle_to((0,1))
        self.img = self.imgs[int(angle)]

    def blit(self):
        screen = self.game.screen
        for i in range(self.n):
            drop = self.dropsx[i], self.dropsy[i]
            screen.blit(self.img, drop)




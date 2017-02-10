import numpy as np
import parameters

class MinMax:

    def __init__(self,couple=None):
        if couple is None:
            self.m = float("inf")
            self.M = -float("inf")
        else:
            self.m = couple[0]
            self.M = couple[1]

    def refresh(self, v):
        if self.m > v:
            self.m = v
        if self.M < v:
            self.M = v

    def __str__(self):
        return str(tuple((self.m, self.M)))

class Statistics:

    def __init__(self, game):
        self.game = game
        self.dist = np.array((0.,0.))
        self.alt = 0.
        self.last_pos = np.copy(game.gui_pos)
        self.last_alt = 0.
        self.mMalt = MinMax()
        self.mMalt.M = 0.
        self.mMtemp = MinMax()
        self.maxSpeed = 0.

    def refresh(self):
        self.dist += np.abs(self.game.campos - self.last_pos)
##        self.dist += np.abs(self.game.gui_pos - self.last_pos)/1. #arbitrary
##        self.dist += np.abs(self.game.pos_int - self.last_pos)
        self.last_pos = np.copy(self.game.campos)
        if not self.game.aboard:
            if self.game.height > parameters.WATER_LEVEL:
                self.alt += abs(self.game.alt_text-self.last_alt)
            self.last_alt = self.game.alt_text
        self.mMalt.refresh(self.game.alt_text)
        self.mMtemp.refresh(self.game.temp_text)
        speed = self.game.controlled.velocity[0]**2 + self.game.controlled.velocity[1]**2
        if speed > self.maxSpeed:
            self.maxSpeed = speed

    def get(self):
        return [("X-distance covered",self.dist[0]/100,"km"), ("Y-distance covered",self.dist[1]/100,"km"),
                 ("Total distance",np.linalg.norm(self.dist/1000.),"km"),
                 ("Total denivelation walked",self.alt/1000,"km"),
                 ("Max. water depth seen",self.mMalt.m,"m"), ("Max. altitude reached",self.mMalt.M,"m"),
                 ("Min. temperature",self.mMtemp.m,"C"), ("Max. temperature",self.mMtemp.M,"C"),
                 ("Max. velocity",self.maxSpeed*10,""),
                 ("Time elapsed",self.game.day,"day")]

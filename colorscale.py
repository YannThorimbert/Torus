import numpy as np
import parameters

S = None

class ColorScale:

    def __init__(self, colors, minval=0.):
        global S
        S = parameters.S
        self.colors = colors
        for i in range(len(self.colors)):
            c1,c2,maxval = self.colors[i]
            if i > 0:
                minval = self.colors[i-1][3]
            delta = maxval - minval
            self.colors[i] = [c1,c2,minval,maxval,delta]

    def get(self, data):
        tot = np.zeros((S,S,3),dtype=int)
        mask = np.zeros((S,S),dtype=bool)
        for c1, c2, m, M, delta in self.colors:
            new_mask = data<M
            current_mask = np.logical_and(new_mask,np.logical_not(mask))
            r = c1[0]
            g = c1[1]
            b = c1[2]
            if delta != 0:
                dmd = (data-m)/delta
                r += dmd*(c2[0]-c1[0])
                g += dmd*(c2[1]-c1[1])
                b += dmd*(c2[2]-c1[2])
            tot[current_mask,0] = r[current_mask]
            tot[current_mask,1] = g[current_mask]
            tot[current_mask,2] = b[current_mask]
            mask = np.logical_or(mask, new_mask)
        return tot


def get_summer():
    return ColorScale([  [(0,0,0), (0,0,100), 0.],                  #0. deep
                         [(0,0,100), (0,30,255), 0.52],             #1. shallow
                         [(0,30,255), (137, 101, 200), 0.598],      #2. sand
                         [(137, 101, 200), (237, 201, 175), parameters.SUMMER_LEVEL],   #3. sand
                         [(237, 201, 175), (50,85,10), 0.603],      #4. sand
                         [(50,85,10), (50,200,50), 0.7],           #5. forest
                         [(50,200,50), (255,255,255), 1.000001],    #6. snow
                         [(255,255,255), (255,255,255), 10.]],      #7. snow
                         minval = -10.)


def get_winter():
    a = (190,190,230)
    b = (200,200,200)
    c = (200,200,230)
    return ColorScale([  [(0,0,0), (0,0,100), 0.],                  #0. deep
                         [(0,0,100), (30,30,150), 0.3],             #shallow
                         [(30,30,150), (50,50,255), parameters.WINTER_LEVEL],
                         [(137,137,219), a, 0.603],
                         [b, c, 0.7],
                         [c, (255,255,255), 1.000001],
                         [(255,255,255), (255,255,255), 10.]],
                         minval = -10.)






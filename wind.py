import numpy as np
import pygame
import thorpy


class Polynomial41D(object):

    def __init__(self, h0, h1, p0, p1):
        dh = h1 - h0
        self.c = np.zeros(4)
        self.c[0] = h0
        self.c[1] = p0
        self.c[2] = 3.*dh - p1 - 2.*p0
        self.c[3] = p0 + p1 - 2.*dh

    def get(self, t):
        return self.c[0] + self.c[1]*t + self.c[2]*t*t + self.c[3]*t*t*t


class Wind:

    def __init__(self, minheights, maxheights, mingrads, maxgrads, periods):
        self.m = minheights
        self.M = maxheights
        self.p = mingrads
        self.P = maxgrads
        self.T = periods
        self.tx, self.ty = 0., 0.
        self.windx = 0.
        self.windy = 0.
        h0,h1,p0,p1 = self.generate_values(0)
        self.currentx = Polynomial41D(h0, h1, p0, p1)
        h0,h1,p0,p1 = self.generate_values(1)
        self.currenty = Polynomial41D(h0, h1, p0, p1)

    def refresh(self):
        if self.tx > self.T[0]:
            h0,h1,p0,p1 = self.generate_values(0)
            self.currentx = Polynomial41D(self.windx, h1, p0, p1)
            self.tx = 0.
        if self.ty > self.T[1]:
            h0,h1,p0,p1 = self.generate_values(1)
            self.currenty = Polynomial41D(self.windy, h1, p0, p1)
            self.ty = 0.
        self.windx = self.currentx.get(self.tx/self.T[0])
        self.windy = self.currenty.get(self.ty/self.T[1])
        self.tx += 1.
        self.ty += 1.

    def generate_values(self,i):
        np.random.seed()
        h0 = self.m[i] + (self.M[i]-self.m[i])*np.random.random()
        h1 = self.m[i] + (self.M[i]-self.m[i])*np.random.random()
        p0 = self.p[i] + (self.P[i]-self.p[i])*np.random.random()
        p1 = self.p[i] + (self.P[i]-self.p[i])*np.random.random()
        return h0, h1, p0, p1

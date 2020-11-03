from opensimplex import opensimplex as simplex
from random import randint
import numpy as np
from PIL import Image
from math import tanh, sqrt

LARGE = 2**64 - 1

def color_map(thresholds, color_tuples):
    def mapper(val, x, y):
        return color_tuples[min(i for i, t in enumerate(thresholds) if t >= tanh(val))]
    return mapper

def island_map(cx=0, cy=0, radius=100):
    def mapper(val, x, y):
        return abs(val * tanh(radius / (((x - cx)**2 + (y - cy)**2)**0.5+1)))
    return mapper

def multiple(*f):
    def apply(val, x, y):
        v = val
        for func in f:
            v = func(v, x, y)
        return v
    return apply

class Map:
    def __init__(self, seed=randint(-LARGE, LARGE), freq=0.5, offset=1000, octaves=1, mapf=lambda v, x, y: v*255):
        self.seed = seed
        if octaves < 1:
            octaves = 1
        self.gens = [simplex.OpenSimplex(seed=seed) for _ in range(octaves)]
        self.octaves = octaves
        self.freq = freq
        self.offset = offset
        self.map = mapf

    def point(self, x, y):
        v = sum(
            gen.noise2d(
                (x*self.freq)*(i+1) + self.offset*(i+1),
                (y*self.freq)*(i+1) + self.offset*(i+1)
            ) * (1/(i+1)) for i, gen in enumerate(self.gens)
        )
        return self.map(v, x, y)

    def line(self, x1, x2, y):
        return [self.point(x, y) for x in range(x1, x2)]

    def area(self, x1, y1, x2, y2):
        return [self.line(x1, x2, y) for y in range(y1, y2)]


if __name__ == "__main__":
    m = Map(freq=0.01, octaves=10, mapf=multiple(island_map(0, 0, radius=20), color_map(
        [0.15, 0.2, 0.3, 0.5, 0.7, 0.9, 1],
        [
            (0,25,150),
            (0, 80, 170),
            (210, 180, 120),
            (0,150,0),
            (0, 100, 0),
            (100,100,100),
            (200, 200, 200)
        ])))
    pixels = m.area(-100, -100, 100, 100)
    print(pixels)
    array = np.array(pixels)
    img = Image.fromarray(np.uint8(array))
    #print(img.tobytes())
    img.save('simplex.png')
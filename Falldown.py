import time
import cv2
import random

class Push(object):
    def __init__(self, init_sx, init_sy, init_ax, init_ay):
        """
        input:
            init_sx: init speed for x axis
            init_sy: init speed for y axis
            init_ax: init acceleration for x axis
            init_ay: init acceleration for y axis
        """
        self.sx = init_sx
        self.sy = init_sy
        self.ax = init_ax
        self.ay = init_ay
        self.t = time.time()

    def run(self, obj):
        """
        obj: the objct that own this mode
        """
        x = obj.cor_x
        y = obj.cor_y
        # assert x, y 

        # get the time and calcute the diffrence of the time. unit in second
        ti = time.time()
        t = ti - self.t
        # compute the movement in x and y axis
        out_x = x + self.sx * t + self.ax * t
        out_y = y + self.sy * t + self.ay * t
        # update the basic attris
        self.sx = self.sx + self.ax * t
        self.sy = self.sy + self.ay * t
        self.t = ti
        # return the new coordinate
        obj.cor_x = out_x
        obj.cor_y = out_y
        return out_x, out_y

class Gravity(Push):
    def __init__(self):

        super(Gravity, self).__init__(0, 0, 0, 9.8)


class Fly(Push):
    def __init__(self):
        s = (random.random()-0.5)*9.8*2
        super(Fly, self).__init__(0, 0, s, 9.8)


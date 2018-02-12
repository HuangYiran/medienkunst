import time
import random
import os
import cv2
import numpy as np
from Falldown import Gravity
from Stone import Stone

class StoneFactory():
    def __init__(self, frq, obj_dir):
        """
        frq: is the frequence of creating the stone, every frq second create a stone
        img_path: the dir of the image object
        last_t: time creating the last stone
        """
        self.frq = frq
        self.last_t = time.time()
        self.objects = []
        self._loadObject(obj_dir)
        self.num_objs = len(self.objects)

    def _loadObject(self, obj_path):
        """
        load the picture of the stone
        """
        for (roots, dirs, files) in os.walk(obj_path):
            for item in files:
                fi = obj_path + '/' + item
                print fi
                img = cv2.imread(fi)
                if not isinstance(img, np.ndarray):
                    print "fail to load this stone, just skip it"
                    continue
                self.objects.append(img)

    def addObject(self, obj_dir):
        self._loadObject(obj_dir)

    #TODO
    def create(self, ti):
        """
        according the last_t, ti and frq decide weather to creat a new stone or not
        """
        if (ti - self.last_t) > self.frq:
            # update the clock
            self.last_t = ti
            # chose a stone from the objects randomly
            index = random.choice(range(self.num_objs))
            img = self.objects[index]
            # here we need a initial coordinate and mode
            init_x = 10
            init_y = 0
            init_m = Gravity()
            stone = Stone(img, init_x, init_y, init_m)
            return stone
        return None 

    def create_abs(self):
        # chose a stone from the objects randomly
        index = random.choice(range(self.num_objs))
        img = self.objects[1]
        # here we need a initial coordinate and mode
        init_x = 10
        init_y = 0
        init_m = Gravity()
        stone = Stone(img, init_x, init_y, init_m)
        return stone


import time
import random
import os
import cv2
from Drawdown import Gravity

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
        self._loadObject(obj_path)
        self.num_objs = len(self.objects)

    def _loadObject(self, obj_path):
        """
        load the picture of the stone
        """
        for item in os.walk(obj_path):
            img = cv2.imread(item)
            self.objects.append(img)

    def addObject(self, obj_dir):
        self._loadObject(obj_dir)

    def create(self, ti):
        """
        according the last_t, ti and frq decide weather to creat a new stone or not
        """
        if (ti - last_t) > frq:
            # update the clock
            last_t = ti
            # chose a stone from the objects randomly
            index = random.choice(self.num_objs)
            img = self.objects[index]
            # here we need a initial coordinate and mode
            init_x = 10
            init_y = 0
            init_m = Gravity()
            stone = Stone(img, init_x, init_y, init_m)
            return stone
        return None 
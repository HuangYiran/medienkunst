import time
import random
import os
import cv2
from Falldown import Gravity, Fly
from Stone import Stone

class StoneFactory():
    def __init__(self, w, obj_dir='./stones', create_probability=0.2, frq=0.5):
        """
        frq: is the frequence of creating the stone, every frq second create a stone
        img_path: the dir of the image object
        last_t: time creating the last stone
        """
        self.frq = frq
        self.probability = create_probability
        self.last_t = time.time()
        self.objects = []
        self._loadObject(obj_dir)
        self.num_objs = len(self.objects)
        self.width_bg = w

    def _loadObject(self, obj_path):
        """
        load the picture of the stone
        """
        for (roots, dirs, files) in os.walk(obj_path):
            for item in files:
                fi = obj_path + '/' + item
                img = cv2.imread(fi)
                self.objects.append(img)
		print(fi)

    def addObject(self, obj_dir):
        self._loadObject(obj_dir)

    #TODO
    def create(self ):
        """
        according the last_t, ti and frq decide weather to creat a new stone or not
        """

        if random.random() < self.probability:

            init_x, init_y = self.create_init_coordinate()
            # chose a stone from the objects randomly
            index = random.choice(range(self.num_objs))
            img = self.objects[index]
            # here we need a initial coordinate and mode
            init_m = Fly()
            stone = Stone(img, init_x, init_y, init_m)
            return stone
        return None 

    def create_abs(self):
        # chose a stone from the objects randomly
        index = random.choice(range(self.num_objs))
        img = self.objects[index]
        # here we need a initial coordinate and mode
        init_x = 10
        init_y = 0
        init_m = Gravity()
        stone = Stone(img, init_x, init_y, init_m)
        return stone

    def create_init_coordinate(self):
        print(self.width_bg)
	l = Stone.get_img_length()
        x = random.random()*(self.width_bg-l)
        y = 0
        return x,y



import cv2
import time
import numpy as np
from StoneFactory import StoneFactory
from Stone import Stone
from Falldown import * 
import utils1 

class Dodger1:
    def __init__(self, batch_size=4):
        """
        input:
            cycle_length: the number of frame, that will be skip, before the next img being processed
            batch_size: the number of frame, that will be processed each time
        """
        self.mode = 1 
        self.batch_size = batch_size
        self.cam = cv2.VideoCapture(0)
        
        # bg is a white wall bg2 is a image background
        self.bg = utils1.bg_init(self.cam, self.mode)
        self.bg2 = cv2.imread('bg/bg1.jpg')
        self.stone_fact = StoneFactory(self.bg2.shape[1])
        self.stones = []
        self.frames = utils1.frames_init(self.cam, batch_size,0.1)
        cv2.namedWindow("window")
        self.debug = True

        print('init finish')

        
    def run(self):
        self.frames = utils1.frames_init(self.cam)
        while True:
            # update frame and extract img
            self.frames = utils1.frames_update(self.cam, self.frames, 0.05)
            img = self.frames[-1]
            # extract player from image
            #player_mask_local = utils1.get_player_mask(img, self.bg)
            #player_mask, _ = utils1.change_coordinate_player(player_mask_local, img, self.bg2)
            #print(player_mask.shape)
            # create stones
            stone = self.stone_fact.create()
            if stone:
                self.stones.append(stone)
            # check hit
            #utils1.check_hit(player_mask, self.stones, self.bg2)
            #display = utils1.combine(img, self.bg2, player_mask_local, self.stones)
            display = utils1.combine(img, self.bg2, None, self.stones)

            if display is None:
                display = img
            #print(display.shape)
            cv2.imshow('', display)
            
            if cv2.waitKey(1) == 27:
                break
        self.cam.release()
        cv2.destroyAllWindows()


if __name__ == '__main__':

    dodger = Dodger1()
    dodger.run()


import cv2
import time
import numpy as np
from StoneFactory import StoneFactory
from Stone import Stone
from Falldown import Gravity
from matplotlib import pyplot as plt # because when i use cv2 to show the image, my laptor corrupt. so i use the plt instead

class Dodger:
    def __init__(self, cycle_length = 100, batch_size = 10):
        """
        input:
            cycle_length: the number of frame, that will be skip, before the next img being processed
            batch_size: the number of frame, that will be processed each time
        """
        self.cycle_length = cycle_length 
        self.batch_size = batch_size
        self.cam = cv2.VideoCapture(0)
        self.bg = self._bg_init() # background
        self.stones = []
        cv2.namedWindow("window")
        self.debug = True

        assert(self.batch_size <= self.cycle_length) # i don't want to precess the null img in the first runing step.

    def _bg_init(self):
        _, img = self.cam.read()
        print("background size: ", img.dtype, img.shape)
        return img

    def set_init(self, img):
        self.bg = img
        
    def run(self):
        stage = 'prepare'
        cnt = 0
        frames = [] # buffer to hold the frames 
        mirror = True # decide weather to display the video or not
        stone_fact = StoneFactory(5, './stones') # the factory to create stone
        #while True:
        while True:
            ret_val, img = self.cam.read() # get the current img from the camera
            if stage is 'prepare':
                # save newest batch_size frames in the frames. and try to do some preparation if necessary
                if cnt < self.cycle_length:
                    # update the frames until reach the edge
                    cnt = cnt+1
                    frames.append(img)
                    if len(frames) > self.batch_size:
                        frames.pop(0)
                else:
                    # reaching the edge. set the stage to the next and initialize other attribs
                    stage = 'running'
                    cnt = 0

            if mirror and stage is 'running':
                img = cv2.flip(img, 1) # ???
                # process the frames to get a representative

                # create a stone if necessary
                #stone = stone_fact.create(time.time)
                if self.debug:
                    print "creating a new stone"
                stone = stone_fact.create_abs()
                if stone:
                    self.stones.append(stone)
                # move the stone if the state is not live, will decrease the countdown value
                if self.debug:
                    print "moving the stone"
                for stone in self.stones:
                    stone.run()
                # check if the stones hit the something: the player or the floor. If so, change its state and img
                if self.debug:
                    print "cheking the stone state"
                self._check_hit(img) # only the stone with state live will be checked
                # when the sate of the stone is not live, start to count down the leben for these stones. remove the stone which countdown==0
                if self.debug:
                    print "removing the dead stone"
                self._remove_stones()
                # add the stone to the image we get from the camera
                if self.debug:
                    print "drawing the stone in the image"
                img = self._combine_stones(img)
                # display the img
                if self.debug:
                    print "displaying the img"
                # cv2.imshow('webcam', img)
                # listen to key esc, when pressed, end the program
            #if cv2.waitKey(1) == 27:
            #    break
            stage = 'prepare'
        self.cam.release()
        cv2.destroyAllWindows()

    def _check_hit(self, img):
        """
        check if the stones hit something: human or floor, if so change the state of the stone and its img
        include three steps:
            1. set a line, only detect the human below this line
            2. get the address of the human
            3. check if stone and human have intersetion
        """
        pass

    def _remove_stones(self):
        self.stones = [stone for stone in self.stones if stone.countdown != 0]

    def _combine_stones(self, img):
        bg = self.bg
        rows_bg, cols_bg, channels_bg = bg.size
        for stone in self.stones:
            fg = stone.get_img()
            add_x, add_y = stone.get_address()
            rows_fg, cols_fg, channels_fg = fg.size
            mask_fg, mask_inv_fg = stone.get_mask()
            if add_x + rows_fg <= rows_bg and add_y + cols_fg <= cols_bg and add_x > 0 and add_y > 0:
                # stone is in the image, try to draw it out in region roi
                roi = img[add_x: x + num_rows, add_y: add_y + num_cols]
                # black out the roi region
                bg_blacked = cv2.bitwise_and(roi, roi, mask = mask_inv_fg)
                # get the stone in the fg(black out the region outside the stone)
                fg_blacked = cv2.bitwise_and(fg, fg, mask = mask_fg)
                # put the stone on the image
                dst = cv2.add(bg_blacked, fg_blacked)
                bg[add_x: x + rows_fg, add_y + cols_fg] = dst
                self.bg = bg
            else:
                print "stone jump out the bound, if it is not dead, set it's state to Dead then process the next stone"
                if stone.get_state() == 'live':
                    stone.set_state('dead')
                continue

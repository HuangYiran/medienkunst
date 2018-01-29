import cv2
import time
import numpy as np
import Stone, StoneFactory, Drawdown

class Dodger():
    def __init__(self, cycle_length = 100, batch_size = 10):
        """
        input:
            cycle_length: the number of frame, that will be skip, before the next img being processed
            batch_size: the number of frame, that will be processed each time
        """
        self.bg = self._bg_init() # backgound
        self.cycle_length = cycle_length 
        self.batch_size = batch_size
        self.cam = cv2.VideoCapture(0)
        self.stone = []

        assert(self.batch_size <= self.cycle_length) # i don't want to precess the null img in the first runing step.

    def _bg_init(self):
        _, img = self.cam.read()
        return img

    def set_init(self, img):
        self.bg = img

    def play(self):
        stage = 'prepare'
        cnt = 0
        frames = [] # buffer to hold the frames 
        mirror = True # decide weather to display the video or not
        stone_fact = StoneFactory(5, './stone') # the factory to create stone
        while True:
            ret_val, img = cam.read() # get the current img from the camera
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
                stone = stone_fact.create(time.time)
                if stone:
                    self.stones.append(stone)
                # move the stone if the state is not live, will decrease the countdown value
                for stone in stones:
                    stone.run()
                # check if the stones hit the something: the player or the floor. If so, change its state and img
                self._check_hit(img) # only the stone with state live will be checked
                # when the sate of the stone is not live, start to count down the leben for these stones. remove the stone which countdown==0
                self._remove_stones()
                # add the stone to the image we get from the camera
                img = self._combine_stones(img)
                # display the img
                cv2.imshow('webcam', img)
                # listen to key esc, when pressed, end the program
                if cv2.waitKey(1) == 27:
                    break
            stage = 'prepare'
        self.cam.release()
        self.cv2.destroyAllWindows()
    def _check_hit(img):
        """
        check if the stones hit something: human or floor, if so change the state of the stone and its img
        """
        pass

    def _remove_stones():
        self.stones = [stone for stone in self.stones if stone.countdown != 0]

    def _combine_stones(img):
        pass

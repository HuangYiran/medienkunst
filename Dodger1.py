import cv2
import time
import numpy as np
from StoneFactory import StoneFactory
from Stone import Stone
from Falldown import * 
from utils1 import *
from matplotlib import pyplot as plt # because when i use cv2 to show the image, my laptor corrupt. so i use the plt instead

class Dodger:
    def __init__(self, mode = 1, cycle_length = 100, batch_size = 10):
        """
        input:
            cycle_length: the number of frame, that will be skip, before the next img being processed
            batch_size: the number of frame, that will be processed each time
        """
        self.mode = mode
        self.cycle_length = cycle_length 
        self.batch_size = batch_size
        self.cam = cv2.VideoCapture(0)
        #self.bg = self._bg_init() # background
        self.bg, self.bg2 = bg_init(self.cam, self.mode)
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
        frames = frames_init(self.cam, self.batch_size) # buffer to hold the frames 
        mirror = True # decide weather to display the video or not
        stone_fact = StoneFactory(5, './stones') # the factory to create stone
        #while True:
        for i in range(1000):
            frames = frames_update(self.cam, frames, self.cycle_length)

            if mirror and stage is 'running':
                # img = cv2.flip(img, 1) # ???
                # create a stone if necessary
                # stone = stone_fact.create(time.time)
                if self.debug:
                    print("current num of stones:", len(self.stones))
                    print "creating a new stone"
                # todo
                stone = stone_fact.create()
                if isinstance(stone, 'list'):
                    self.stones.extend(stone)
                else:
                    self.stones.append(stone)
                # move the stone if the state is not live, will decrease the countdown value
                if self.debug:
                    print "moving the stone"
                for stone in self.stones:
                    stone.run()
                # process the frame to get a representative
                if self.debug:
                    print "prepare the img"
                img = self._prepare_img(frames)
                # check if the stones hit the something: the player or the floor. If so, change its state and img
                if self.debug:
                    print "cheking the stone state"
                # self._check_hit(img) # only the stone with state live will be checked
                mask_player = get_player_mask(img, self.bg)
                mask_player = change_coordinate(mask_player, self.bg2, self.mode)
                check_hit(mask_player,  self.stones)
                # when the sate of the stone is not live, start to count down the leben for these stones. remove the stone which countdown==0
                if self.debug:
                    print "removing the dead stone"
                self._remove_stones()
                # add the stone to the image we get from the camera
                if self.debug:
                    print "drawing the stone in the image"
                # img = self._combine_stones(img)
                img = combine(bg, bg2, mask_player, self.stones, mode)
                # display the img
                if self.debug:
                    print "displaying the img"
                cv2.imshow('window', img)
                #plt.imshow(img)
                #plt.show()
                # listen to key esc, when pressed, end the program
                #time.sleep(1)
            if cv2.waitKey(1) == 27:
                break
        stage = 'prepare'
        self.cam.release()
        cv2.destroyAllWindows()

    def _prepare_img(self, frames):
        """
        process the frames to get a representative
        return img
        """
        return frames[-1]

    def _check_hit(self, img):
        """
        check if the stones hit something: human or floor, if so change the state of the stone and its img
        include three steps:
            1. set a line, only detect the human below this line
            2. get the address of the human
            3. check if stone and human have intersetion
        """
        # set the line
        line = int(round(0.3 * img.shape[0]))
        # get the roi of the player
        mask_player = self._get_playermask(img, line)
        threshold = 100
        for stone in self.stones:
            # only process the stone with the state 'live'
            if stone.get_state() != 'live':
                continue
            # black out the background of the stone picture
            img_stone = stone.get_img()
            _, mask_inv_stone = stone.get_mask()
            img_stone = cv2.bitwise_and(img_stone, 0, mask = mask_inv_stone)
            # create a blackboard
            blackboard = np.zeros(self.bg.shape, np.uint8)
            # draw the stone of the balckboard
            img_blackboard = self._combine_stone(blackboard, stone)
            # get the image in the roi of player
            if self.debug:
                print("player_mask: ", mask_player, mask_player.shape)
            img_shot = cv2.bitwise_and(img_blackboard, img_blackboard, mask = mask_player)
            # check collision
            if np.sum(img_shot) > threshold:
                print "stone hit"
                stone.set_state('win')

    def _img_sub(self, img1, img2):
        """
        return |img1 - img2|
        """
        shape_img1 = img1.shape
        shape_img2 = img2.shape
        assert(shape_img1 == shape_img2)
        img1 = img1.reshape([-1])
        img2 = img2.reshape([-1])
        diff = np.array(map(self._uint8_abs_sub, img1, img2), dtype = 'uint8')
        diff = diff.reshape(shape_img1)
        return diff

    def _uint8_abs_sub(self, v1, v2):
        """
        return |v1 - v2|
        """
        if v1 > v2:
            return v1 - v2
        else:
            return v2 - v1

    def _get_playermask(self, img, line):
        """
        only recognize the player under the line
        pay attention that, the return mask should be size of img. not only the part under the line
        """
        fg = img
        rows_bg, cols_bg, channels_bg = self.bg.shape
        rows_fg, cols_fg, channels_fg = fg.shape
        assert(cols_bg == cols_fg)
        # only check the area under the line
        bg = self.bg[rows_bg - line: rows_bg]
        fg = fg[rows_bg - line: rows_fg]
        # get the difference between the bg and fg
        gray_bg = cv2.cvtColor(bg, cv2.COLOR_BGR2GRAY)
        gray_fg = cv2.cvtColor(fg, cv2.COLOR_BGR2GRAY)
        gray_diff = self._img_sub(gray_bg, gray_fg)
        if self.debug:
            print('line: ', line)
            print('gray_fg: ', gray_fg)
            print('gray_bg: ', gray_bg)
            print('gray_diff:', gray_diff)
        ret, mask = cv2.threshold(gray_diff, 30, 255, cv2.THRESH_BINARY)
        # set the kernel for opening and closing
        kernel = np.ones((5, 5), np.uint8)
        mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, kernel)
        mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, kernel)
        # put this part of mask into the img's mask
        mask_img = np.zeros([rows_bg, cols_bg], dtype = 'uint8')
        mask_img[rows_bg - line: rows_bg] = mask
        return mask_img

    def _remove_stones(self):
        self.stones = [stone for stone in self.stones if stone.countdown != 0]

    def _combine_stones(self, img):
        bg = img
        rows_bg, cols_bg, channels_bg = bg.shape
        for stone in self.stones:
            bg = self._combine_stone(bg, stone)
        return bg

    def _combine_stone(self, bg, stone):
        rows_bg, cols_bg, channels_bg = bg.shape
        fg = stone.get_img()
        add_x, add_y = stone.get_address()
        rows_fg, cols_fg, channels_fg = fg.shape
        mask_fg, mask_inv_fg = stone.get_mask()
        if add_x + rows_fg <= rows_bg and add_y + cols_fg <= cols_bg and add_x >= 0 and add_y >= 0: # ?????the condition here is false, only for test
            # stone is in the image, try to draw it out in region roi
            roi = bg[add_x: add_x + rows_fg, add_y: add_y + cols_fg]
            # black out the roi region with mask
            bg_blacked = cv2.bitwise_and(roi, roi, mask = mask_inv_fg)
            # get the stone in the fg(black out the region outside the stone)
            fg_blacked = cv2.bitwise_and(fg, fg, mask = mask_fg)
            # put the stone on the image
            dst = cv2.add(bg_blacked, fg_blacked)
            bg[add_x: add_x + rows_fg, add_y: add_y + cols_fg] = dst
        else:
            print "stone jump out the bound, if it is not dead, set it's state to Dead then process the next stone"
            print("address of stone: ", (add_x, add_y), "size of the stone", stone.get_size())
            print('boudary of the background:', (rows_bg, cols_bg))
            if stone.get_state() == 'live':
                stone.set_state('dead')
        return bg


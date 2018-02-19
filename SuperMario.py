#-*- coding: utf-8 -*-
import cv2
import numpy as np
import math
import time
import pyautogui as pg
import threading
import  Queue

from utils0 import *

class SuperMario:
    def __init__(self):
        # init cam and subtractor
        self.cam = cv2.VideoCapture(0)
        #self.bs = cv2.createBackgroundSubtractorKNN(detectShadows = False)
        self.bs = cv2.createBackgroundSubtractorMOG2(history=50, detectShadows=False)
        self.bs.setHistory(200)
        cv2.namedWindow('snowbros', 0)
        cv2.namedWindow('rect', 0)
        cv2.namedWindow('rect_cond', 0)
        cv2.namedWindow('mask_before', 0)
        #cv2.namedWindow('mask_after', 0)
        #cv2.namedWindow('intr', 0)
        #cv2.namedWindow('outer', 0)
        cv2.resizeWindow('snowbros', 640, 480)
        cv2.resizeWindow('rect', 640, 480)
        cv2.resizeWindow('rect_cond', 640, 480)
        cv2.resizeWindow('mask_before', 640, 480)
        #cv2.resizeWindow('mask_after', 640, 480)
        #cv2.resizeWindow('intr', 640, 480)
        #cv2.resizeWindow('outer', 640, 480)

        # get the boundary of the game
        self.max_history = 10

        # save the history data
        self.histories = [] # rect history
        ret, img = self.cam.read()
        if ret:
            self.h, self.w, _= img.shape
        else:
            print '>>>>>>>> fuck error'

        # get fixed_contour
        self.f_rect = self._get_fixed_rect()

        # set the large of the noise rect
        self.threshold_rect = 200 * 200

        # set the move queue for the threading 
        self.queue_move = Queue.Queue(maxsize = 1)
        self.queue_move.put('stay')

        # init the game
        # self._sb_init()

        # set up the threads: control and action capture
        self.thread_control = threading.Thread(target = self._control_game, args = ())
        
        # set the thred lock
        self.mutex = threading.Lock()

    def run(self):
        self._sb_init()
        self.thread_control.start()
        self._action_capture()

    def _action_capture(self):
        while True:
            img = self._get_next_img()
            rects = self._get_player_rects(img)
            #rects = self._remove_noise_rect(self.f_rect, rects) # remove the rect outside the f_rect
            num_rects = len(rects)
            if num_rects == 0:
                continue
            elif num_rects != 1:
                rect = self._get_largest_rect(rects)
            else:
                rect = rects[0]
            rect = self._optimize_rect(rect)
            print('to display the rect', time.time())
            # display
            #print "+++show the largest rect"
            self._show_rect(rect, 'rect')
            #print "+++show the condition rect"
            self._show_rect(self.f_rect, 'rect_cond')
            # if the largest rect is too small, set the move according to the history
            if rect[2]*rect[3] < self.threshold_rect:
                move = 'stay'
            else:
                self._update_histories(rect)
                move = self._get_player_move(self.f_rect, rect)
            # move the fixed rect
            #self.f_rect = self._move_fixed_rect(self.f_rect, rect, move)
            # set the move to the queue
            self.mutex.acquire()
            if not self.queue_move.empty():
                self.queue_move.get()
            self.queue_move.put(move)
            self.mutex.release()
            print("time and move", time.time(), move)
            if cv2.waitKey(1) == 27:
                self._sb_init()

    def _sb_init(self):
        # get player rects in the img, we may get lots of rects but only one of them is the right one
        counter = 5
        while counter >= 0:
            print '================ try new img ==================='
            _, img = self.cam.read()
            #cv2.imshow('supermario', img)
            player_rects = self._get_player_rects(img)
            if len(player_rects) == 0:
                continue
            player_rect = self._get_largest_rect(player_rects)
            player_rect = self._optimize_rect(player_rect)
            self._update_histories(player_rect)
            combined_rect = self._combine_rect(self.f_rect, player_rect)
            cv2.imshow('rect', combined_rect)
            """
            if self._check_fixed_rect(player_rect):
                print '++++ got one'
                counter = counter - 1
            else:
                print '---- ohh no reset it'
                counter = 5
            """
            if cv2.waitKey(1) == 27:
                break
        pg.press('enter')

    def _combine_rect(self, f_rect, rect):
        mask_f_rect = np.zeros((self.h, self.w), dtype = 'uint8')
        mask_rect = np.zeros((self.h, self.w), dtype = 'uint8')
        mask_f_rect[f_rect[1]:f_rect[1] + f_rect[3], f_rect[0]:f_rect[0]+f_rect[2]] =  255
        mask_rect[rect[1]:rect[1] + rect[3], rect[0]:rect[0]+rect[2]] = 127
        combined = cv2.addWeighted(mask_f_rect, 0.4, mask_rect, 0.6, 0)
        return combined

    def _control_game(self):
        """
        control the game with the move
        """
        while True:
            # get the move
            self.mutex.acquire()
            if self.queue_move.empty():
                print "<<<<<the queue is empty, fuck."
                continue
            move = self.queue_move.get()
            self.mutex.release()
            print('control time and move:', time.time(), move)
            # control the game 
            # pg.press('x')
            if move == 'stay' or move == 'sit':
                pg.keyUp('left')
                pg.keyUp('right')
                pg.press('x')
            elif move == 'left':
                print 'press left'
                pg.press('x')
                pg.keyUp('right')
                pg.keyDown('left')
            elif move == 'right':
                print 'press right'
                pg.press('x')
                pg.keyUp('left')
                pg.keyDown('right')
            elif move == 'jump':
                print 'press jump'
                pg.press('x')
                pg.press('z')
            elif move == 'left_jump':
                print 'press left jump'
                pg.press('z')
                pg.press('x')
                pg.keyUp('right')
                pg.keyDown('left')
            elif move == 'right_jump':
                print 'press right jump'
                pg.press('z')
                pg.press('x')
                pg.keyUp('left')
                pg.keyDown('right')
            else:
                pg.press('x')

            # if we don't have a new move from the action capture, use the current move in the next round
            self.mutex.acquire()
            if self.queue_move.empty():
                self.queue_move.put(move)
            self.mutex.release()

    def _get_fixed_rect(self):
        # set the threshold
        t_left = 0.3
        t_right = 0.6
        t_head = 0.3
        t_foot = 0.8
        rect_cond = (int(t_left * self.w), int(t_head * self.h), int((t_right - t_left) * self.w), int((t_foot - t_head) * self.h))
        return rect_cond

    def _check_fixed_rect(self, rect):
        # set the threshold
        t_left = 0.3
        t_right = 0.6
        t_head = 0.2
        t_foot = 0.8
        x, y, w, h = rect[0], rect[1], rect[2], rect[3]
        rect_cond = (int(t_left * self.w), int(t_head * self.h), int((t_right - t_left) * self.w), int((t_foot - t_head) * self.h))
        print '>>>>>>>>>>> show condition rect'
        self._show_rect(rect_cond, 'rect_cond')
        if x > t_left * self.w and x + w < t_right * self.w and y > t_head * self.h and y + h > t_foot * self.h:
            return True
        return False

    def _get_largest_rect(self, rects):
        area = 0
        if isinstance(rects[0], int):
            rect_target = rects
        else:
            for rect in rects:
                if isinstance(rect, int):
                    break
                if rect[2]*rect[3] > area:
                    area = rect[2] * rect[3]
                    rect_target = rect
        return rect_target

    def _show_rect(self, rect, window = 'rect'):
        rt = np.zeros((self.h, self.w), dtype = 'uint8')
        #print '#### in show_rect'
        #print("rt.shape:", rt.shape)
        #print("rect.size", rect)
        rt[rect[1]: rect[1]+rect[3], rect[0]: rect[0]+rect[2]] = 255
        cv2.imshow(window, rt)
        if cv2.waitKey(1) == 27:
            print 'byebye'
        #print '#### end show_rect'

    def _get_next_img(self):
        return self.cam.read()[1]

    def _get_player_rects(self, img):
        player_mask = self.bs.apply(img)
        # transform the mask
        player_mask = cv2.flip(player_mask, flipCode = 1)
        # optimize the mask
        kernel = np.ones((5, 5), np.uint8)
        ret, player_mask = cv2.threshold(player_mask, 177, 255, 0)
        player_mask = cv2.morphologyEx(player_mask, cv2.MORPH_CLOSE, kernel)
        player_mask = cv2.dilate(player_mask, cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (3, 3)), iterations=2)
        player_mask = cv2.morphologyEx(player_mask, cv2.MORPH_OPEN, kernel)
        player_mask = cv2.dilate(player_mask, cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (3, 3)), iterations=2)
        #try:
        #    player_mask = cv2.convexHull(player_mask)
        #except:
        #    print '<<<<<< unable to get the Hull of the player mask'
        # >>>>>>>>>> output player mask 
        cv2.imshow('mask_before', player_mask)
        cv2.imwrite('1.png', player_mask)
        # get the boundary of the player in the image 
        _, contours, _ = cv2.findContours(player_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        rects = []
        for cont in contours:
            # expected the item of the rects to be tuple, but ....
            rects.append(cv2.boundingRect(cont))
        #print('len(rects)', len(rects))
        if len(rects) == 0:
            print ">>>>>>>>>>>>>>>>>>>>fuck, error. len(rects) == 0"
        return rects

    def _remove_noise_rect(self, f_rect, rects):
        """
        remove the conts, which are not related to the fixed contour.
        As output, we only the cont, that fit the fixed contour most.
        method??: get the intersection between the fixed contour and given cont, and return the cont, that has the largest intersection.
        conditon of the method is, the conts we get from the _get_player_contours should be good.
        """
        inter = 0
        rect_t = []
        for rect in rects:
            if isinstance(rect, int):
                break;
            inter_tmp, _ = self._get_intersection_rect(f_rect, rect)
            if inter_tmp > inter:
                rect_t.append(rect)
        return rect_t

    def _get_intersection_rect(self, f_rect, rect):
        """
        get the intersection of two rects
        method: use the mask to get the intersection
        if they have no intersection, the outer-section should be mask_rect
        output: intersection and outer-section
        """
        # get the mask of fixed rect and rect
        mask_f_rect = np.zeros((self.h, self.w), dtype = 'uint8')
        mask_rect = np.zeros((self.h, self.w), dtype = 'uint8')
        mask_f_rect[f_rect[1]:f_rect[1] + f_rect[3], f_rect[0]:f_rect[0]+f_rect[2]] =  255
        mask_rect[rect[1]:rect[1] + rect[3], rect[0]:rect[0]+rect[2]] = 255
        # calculate the intersection and outer-section
        intr = cv2.bitwise_and(mask_f_rect, mask_f_rect, mask = mask_rect)
        outer = cv2.bitwise_xor(intr, mask_rect, mask_rect)
        intr = np.sum(intr)
        outer = np.sum(outer)
        return intr, outer

    def _get_player_move(self, f_rect, rect):
        """
        use the fixed rect and the given rect to detect the control order of the player
        the orders include: move left, move right, jump, jump down and stay, rightjump, leftjump
        input:
            f_rect:tuple. 0:x, 1:y, 2:w, 3:h
            rect:tuple
        output:
            string
        """
        # set threthold for different moves
        t_stay = 1/9
        t_left = 17
        t_right = 17
        t_jump_foot = 100
        t_jump_head = 10
        t_sit_foot = 20
        t_sit_head = 300
        # get the intersection of two rects
        intr, outer = self._get_intersection_rect(f_rect, rect)
        if intr == 0:
            # calcu the distant between two rects, ???
            if self._check_move_left_part2(f_rect, rect, t_left):
                return 'left'
            elif self._check_move_right_part2(f_rect, rect, t_right):
                return 'right'
        elif outer == 0: #or outer/intr < t_stay:
            # action stay other jump down other jump§
            if self._check_sit(f_rect, rect, t_sit_foot, t_sit_head):
                return 'sit'
            elif self._check_jump(f_rect, rect, t_jump_foot, t_jump_head):
                return 'jump'
            else:
                return 'stay'
        else:
            # ationmove left, right other jump
            if self._check_cover(f_rect, rect):
                return 'unknown'
            if self._check_move_left_part1(f_rect, rect, t_left):
                if self._check_jump(f_rect, rect, t_jump_head, t_jump_foot):
                    return 'left_jump'
                else:
                    return 'left'
            elif self._check_move_right_part1(f_rect, rect, t_right):
                if self._check_jump(f_rect, rect, t_jump_head, t_jump_foot):
                    return 'right_jump'
                else:
                    return 'right'
            elif self._check_move_left_part2(f_rect, rect, t_left):
                if self._check_jump(f_rect, rect, t_jump_head, t_jump_foot):
                    return 'left_jump'
                else:
                    return 'left'
            elif self._check_move_right_part2(f_rect, rect, t_right):
                if self._check_jump(f_rect, rect, t_jump_head, t_jump_foot):
                    return 'right_jump'
                else:
                    return 'right'
            elif self._check_jump(f_rect, rect, t_jump_head, t_jump_foot):
                return 'jump'
            else:
                return 'unknown'

    def _check_cover(self, f_rect, rect):
        x1, y1, w1, h1 = f_rect[0], f_rect[1], f_rect[2], f_rect[3]
        x2, y2, w2, h2 = rect[0], rect[1], rect[2], rect[3]
        #print '---check cover: x2 < x1 and x2 + w2 > x1 + w1'
        if x2+10 < x1 and x2 + w2-10  > x1 + w1:
            return True
        else:
            return False

    def _check_move_left_part1(self, f_rect, rect, t_left):
        #print '---check move left'
        #print('x, f_x', rect[0], f_rect[0])
        if len(self.histories)>3:
            last_rect = self.histories[-3]
            print("x1,x2:", last_rect[0], rect[0])
            if  last_rect[0] - rect[0] > t_left:
                return True
        return False

    def _check_move_left_part2(self, f_rect, rect, t_left):
        if rect[0] < f_rect[0]:
            return True
        return False

    def _check_move_right_part1(self, f_rect, rect, t_right):
        #print '---check move right'
        #print('x + w, f_x + f_w', rect[0]+rect[2], f_rect[0]+f_rect[2])
        if len(self.histories)>3:
            last_rect = self.histories[-3]
            if rect[0] - last_rect[0] > t_right:
                return True
        return False

    def _check_move_right_part2(self, f_rect, rect, t_rect):
        if rect[0] + rect[2] > f_rect[0] + f_rect[2]:
            return True
        return False


    def _check_jump(self, f_rect, rect, t_jump_head, t_jump_foot):
        x1, y1, w1, h1 = f_rect[0], f_rect[1], f_rect[2], f_rect[3]
        x2, y2, w2, h2 = rect[0], rect[1], rect[2], rect[3]
        #print '---check jump: y1 - y2 > t_jump_head'
        #print('y1-y2', y1-y2)
        #print('threshold foot, head', t_jump_foot, t_jump_head)
        if y1 - y2 > t_jump_head:
            return True
        return False

    def _check_sit(self, f_rect, rect, t_sit_head, t_sit_foot):
        x1, y1, w1, h1 = f_rect[0], f_rect[1], f_rect[2], f_rect[3]
        x2, y2, w2, h2 = rect[0], rect[1], rect[2], rect[3]
        #print '---check sit: (y2 + h2) - (y1 + h1) > t_sit_foot and y2 - y1 < t_sit_head'
        #print('(y2 + h2)-(y1 + h1), y2 - y1', (y2 + h2)-(y1 + h1), y2-y1)
        #print('threshold foot, head', t_sit_foot, t_sit_head)
        if (y2 + h2) - (y1 + h1) > t_sit_foot and y2 - y1 < t_sit_head:
            return True
        return False

    def _move_fixed_rect(self, f_rect, rect, move):
        """
        move the fixed_rect to pass the player according to the move of the player
        action of player:
            left: move left till x1 = x2
            right: move right till x1 + w1 = x2 + w2
            jump: stay still
            sit: stay still
            rightjump: move left till x1 = x2
            leftjump: move right till x1 + w1 = x2 + w2
            stay: stay still
        """
        x1, y1, w1, h1 = f_rect[0], f_rect[1], f_rect[2], f_rect[3]
        x2, y2, w2, h2 = rect[0], rect[1], rect[2], rect[3]
        if move == 'jump' or move == 'sit' or move == 'stay':
            pass
        elif move == 'left' or move == 'left_jump':
            x1 = int(x1 - (x1 - x2)/2)
        elif move == 'right' or move == 'right_jump':
            x1 = int(x1 + (x2 + w2 - x1 - w1)/2)
        else:
            print "<<<<<<unrecognize action"
        return (x1, y1, w1, h1)

    def _optimize_rect(self, rect, method = 'lambda_return'):
        if method == 'average':
            return self._optimize_rect_average(rect)
        elif method == 'lambda_return':
            return self._optimize_rect_lambda_return(rect)
        else:
            print 'no method found, return the original rect'
            return rect

    def _optimize_rect_average(self, rect):
        """
        use the history data to optimize the rect
        method1: get averate simplily
        """
        num_history = len(self.histories)
        aver_x = 0
        aver_y = 0
        aver_w = 0
        aver_h = 0
        if num_history == 0:
            return rect
        else:
            print("num_history: ",num_history)
            for i in range(num_history):
                print self.histories[i]
                aver_x = aver_x + self.histories[i][0]
                aver_y = aver_y + self.histories[i][1]
                aver_w = aver_w + self.histories[i][2]
                aver_h = aver_h + self.histories[i][3]
            aver_x = aver_x + rect[0]
            aver_y = aver_y + rect[1]
            aver_w = aver_w + rect[2]
            aver_h = aver_h + rect[3]
            aver_x = int(aver_x / (1 + num_history))
            aver_y = int(aver_y / (1 + num_history))
            aver_w = int(aver_w / (1 + num_history))
            aver_h = int(aver_h / (1 + num_history))
        return (aver_x, aver_y, aver_w, aver_h)

    def _optimize_rect_lambda_return(self, rect):
        """
        use the history data to optimize the rect
        input: the rect to be optimized
        output: the optimized rect
        method1: get average simplily
        method2: lambda return 
        """
        lamb= 0.9
        mal_items = []
        tmp = 1
        num_history = len(self.histories)
        if len(self.histories) == 0:
            return rect
        else:
            for i in range(num_history):
                tmp = tmp * lamb
                mal_items.append(tmp)
            summer_x = 0
            summer_y = 0
            summer_w = 0
            summer_h = 0
            for i in range(num_history)[::-1]:
                summer_x = summer_x + (1 - lamb) * mal_items[i] * self.histories[i][0]
                summer_y = summer_y + (1 - lamb) * mal_items[i] * self.histories[i][1]
                summer_w = summer_w + (1 - lamb) * mal_items[i] * self.histories[i][2]
                summer_h = summer_h + (1 - lamb) * mal_items[i] * self.histories[i][3]
            summer_x = summer_x + mal_items[-1] * rect[0]
            summer_y = summer_y + mal_items[-1] * rect[1]
            summer_w = summer_h + mal_items[-1] * rect[2]
            summer_h = summer_h + mal_items[-1] * rect[3]
            return (int(summer_x), int(summer_y), int(summer_w), int(summer_h))


    def _update_histories(self, rect):
        if len(self.histories) >= self.max_history:
            self.histories.pop(0)
        self.histories.append(rect)


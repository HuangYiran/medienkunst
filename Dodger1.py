import cv2
import time
import numpy as np
from StoneFactory import StoneFactory
from Stone import Stone
from Falldown import * 
import utils1 
import threading
from Queue import Queue
from Player import Player
from TextBoard import TextBoard

class Dodger1():
    def __init__(self, batch_size=4):
        """
        input:
            cycle_length: the number of frame, that will be skip, before the next img being processed
            batch_size: the number of frame, that will be processed each time
        """
	
	self.resize_ratio = 0.25
        self.mode = 1 
        self.batch_size = batch_size
        self.status = 'init'
        

        self.cam = cv2.VideoCapture(0)
	#self.bs = cv2.createBackgroundSubtractorMOG2(history=50, detectShadows=False)
	
        
        # bg is a white wall bg2 is a image background
        self.bg2 = cv2.imread('bg/bg1.jpg')

        self.text_board = TextBoard(self.bg2)
        self.stone_fact = StoneFactory(self.bg2.shape[1])
        self.stones = []
        self.image = Queue(maxsize=1)
        #self.bg = utils1.bg_init(self.cam,self.image)
	self.bg = cv2.imread('test/bg_init.png')
	if self.resize_ratio != 0:
	    self.bg2 = cv2.resize(self.bg2,None,fx=self.resize_ratio, fy=self.resize_ratio)
	    self.bg = cv2.resize(self.bg,None,fx=self.resize_ratio, fy=self.resize_ratio)
        self.frames = utils1.frames_init(self.cam, self.image, self.resize_ratio, batch_size,0.1)
        img = self.frames[-1]
        # self.bg = img
        self.player = Player(self.bg2, img)
        self.debug = True
        self.time = time.time()
	
        print('init finish')




        
    def run(self, q):
        self.get_running_time(1)
        self.frames = utils1.frames_init(self.cam, self.image, self.resize_ratio)
        self.get_running_time(2)
	cv2.namedWindow("FullScreen", cv2.WINDOW_NORMAL) 
	cv2.setWindowProperty("FullScreen", cv2.WND_PROP_FULLSCREEN,cv2.WINDOW_FULLSCREEN)
        time.sleep(2)
        while True:
            if self.status == 'init':
                display = self.bg2
                self.status = 'begin'

            if self.status == 'begin':
                display, cnt = self.text_board.count_down()
                if cnt==0:
                    self.status = 'run'

            elif self.status == 'run':
                bg2 = self.bg2.copy()
                self.get_running_time(3)
                _, img = self.cam.read()
                img = cv2.resize(img,None,fx=self.resize_ratio, fy=self.resize_ratio)
                #print img.shape
                img = cv2.flip(img,1)
                self.frames = utils1.frames_update(self.frames, img)
                
                img = utils1.get_avg_img(self.frames)
                #cv2.imwrite('./test/avg_img.png', img)
                self.get_running_time(4)
                # img = self.frames[-1]
                # print img.shape
                if not q.empty():
                    q.get()
                q.put(img)
                # extract player from image
                #player_mask_local = utils1.get_player_mask(img, self.bg)
                #player_mask, _ = utils1.change_coordinate_player(player_mask_local, img, self.bg2)
                #print(player_mask.shape)
                # create stones

                stone = self.stone_fact.create()
                if stone:
                    self.stones.append(stone)
                #cv2.imwrite('./test/img.png', img)
                #diff_mask = utils1.get_diff_mask(self.frames)
                #diff_mask = self.bs.apply(img)
                #cv2.imwrite('./test/diff_mask.png', diff_mask)
                bg2 = self.player.draw_bg(self.bg, bg2, img)
                # local mask
                player_mask = self.player.get_mask(img, self.bg)
                # global mask
                player_mask = self.player.get_global_mask(self.bg2, player_mask)
                #player_mask = (player_mask*255).astype('uint8')
                #cv2.imwrite('./test/player_mask.png', player_mask)



                self.get_running_time(5)
                
                #display = utils1.combine(img, self.bg2, player_mask_local, self.stones)

                display, self.stones = utils1.combine(img, bg2, player_mask, self.stones)
                self.get_running_time(6)

                if display is None:
                    display = img
                #cv2.imwrite('./test/display.png', display)
                #print(display.shape)
                #print(type(display[0][0][0]))
                display = display.astype('uint8')

                del bg2
            cv2.imshow('FullScreen', display)
            del display
            if cv2.waitKey(1) == 27:
                break
        self.cam.release()
        cv2.destroyAllWindows()

          


    def get_running_time(self,i):
        print(str(i)+':'+str(time.time()-self.time))
        self.time = time.time()



class UpdateBG:
    def __init__(self, frames_l=5, delay=5):
        self.frames_l =  frames_l
        self.delay = delay
        



    
    def get_bg(self, q):
        while True:
            if q.empty():
                print('empty')
                continue
            else:
                print('here')
                bg = utils1.bg_init(None, q, self.frames_l, self.delay)


    

if __name__ == '__main__':

    dodger = Dodger1()
    update_bg = UpdateBG()

    img_q = Queue(maxsize=1)

    t1 = threading.Thread(target=dodger.run, args=(img_q,))
    #t2 = threading.Thread(target=update_bg.get_bg, args=(img_q,))
    t1.start()
    #t2.start()

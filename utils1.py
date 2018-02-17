import time
import numpy as np
from six.moves import xrange
import cv2
from StoneFactory import StoneFactory
def bg_init(cam, img_q=None, frames_l=5, delay=2):
    """
    init the background of the game
    input:
        cam: instance of the camera 
        mode: the mode of the game 
            0: use the raw background
            1: use the whiteboard as the background
    retun:
        bg: type of ndarray 
        bg2: background for mode1
    """
    stabil = False
    color_threshold = (10, 10, 10)
    percentage_threshold = 0.999
    bg = None
    bg_cans = []
    
    frames = frames_init(cam, img_q, frames_l, delay)
    # print(frames[0])
    x, y, z = frames[0].shape
    area = x*y

    mask_r = np.zeros((x, y))
    bg = np.zeros((x, y, z))

    while not stabil:

        t = np.vstack(frames)
        l = len(frames)
        t = t.reshape(l, x, y, z)
        t = 1.0*np.sum(t, axis=0)/l
        # print(t.shape)
        if len(bg_cans) > 0:
            pre = bg_cans[-1]
            diff = t-pre

            diff = np.power(diff, 2)
            # print(diff[0][0])
            # print(diff.shape)
            mask = diff<color_threshold
            mask = mask.astype(int)
            mask = np.prod(mask, 2)
            new_mask = mask-mask_r
            # print(new_mask)
            addition_mask = new_mask==1
            
            addition_mask = addition_mask.astype(int)
            t_mask = addition_mask
            #print(np.sum(addition_mask*mask_r))
            addition_mask = np.repeat(addition_mask.astype(int),3).reshape(x,y,z)
            addition_img = t*addition_mask
            mask_r += t_mask
            mask_r = mask_r.astype(int)
            bg = bg+addition_img
            bg = bg.astype('uint8')
            #print(masked.shape, area)

            correct = 1.0*np.count_nonzero(mask_r)/area
            print(correct)

            # if the correct points in frames is bigger than required percentage 
            # we think its a proper background
            if correct > percentage_threshold:
                stabil = True
                return bg
            bg_cans[-1] = t
        else:
            bg_cans.append(t)
        frames = frames_init(cam, img_q, frames_l, delay)


        cv2.imwrite('./test/bg_init.png', bg)

    print('background init succeed')
    return bg

            

        

    pass

def frames_init(cam, img_q, resize=0.5, batch_size=3, time_interval=0.1):
    """
    init the original frame list
    input:
        cam: instance of the camera
        batch_size: the number of frame in the list
    output:
        frames: output the list of the frame
    """
    l = []
    for i in xrange(batch_size):
        if not img_q.empty():
            # print(image)
            image = img_q.get()
	    print image.shape
            l.append(image)
        else:
            _, img = cam.read()
	    if resize != 0:
	        img = cv2.resize(img,None,fx=resize, fy=resize)
	    img = cv2.flip(img,1)
	    print img.shape
            l.append(img)
        time.sleep(time_interval)
    return l

def get_player_mask(img, bg):
    """
    the the mask of the player rio
    input:
        img: the image getting from the frames
        bg: the background of the game 
    output:
        mask_player
    """
    color_threshold = (400, 400, 400) # threshold for squared matrix
    diff_sqr = np.power(img - bg, 2)
    masked = diff_sqr>color_threshold
    masked = np.prod(masked,axis=2)
    return masked



def _remove_stones(stones):
    stones = [stone for stone in stones if stone.countdown != 0]
    return stones

def combine(img, bg2, player_mask, stones):
    """
    input:
        img: the imgage getting from the frames
        bg2: the background of mode 1
        mask_player: the mask for the player
        stones: the list of the stones
        mode: the mode of the game
    output:
        img
    """
       
    result = bg2


    # combine stone
    for stone in stones:
        result = stone.draw_in_bg(result, player_mask)
    stones = _remove_stones(stones)

    #cv2.imwrite('./test/stone_mask.png', result)
    return result, stones


def frames_update(frames, img):
    """
    update the img in the frame list
    input:
        cam: instance of the camera
        frames: frame list to store the frame
        cycle_length: frequece to update the frame output: frames """ 
    
    frames.append(img)
    frames.pop(0)
    return frames

def get_avg_img(frames):
    x, y, z = frames[0].shape
    t = np.vstack(frames)
    l = len(frames)
    t = t.reshape(l, x, y, z)
    t = 1.0*np.sum(t, axis=0)/l
    return t

def get_diff_mask(frames):
    if len(frames)>2:
	
	threshold = (3000,3000,3000)
	m = int(len(frames)/2)
	frame1 = get_avg_img(frames[:m])
	frame2 = get_avg_img(frames[m:])
	diff = 1.0*frame2-1.0*frame1
	m,n,_ = diff.shape
	diff = np.power(diff, 2)
	mask = diff>threshold
	t1 = mask[:,:,0:1].astype(int)
	t2 = mask[:,:,1:2].astype(int)
	t3 = mask[:,:,2:3].astype(int)
	mask = t1+t2+t3
	mask = ((mask>0).reshape(m,n)*255).astype('uint8')
	
	return mask

if __name__ == '__main__':
            
    #cv2.imwrite('./test/stone_mask1.png', stone_img)

    cam = cv2.VideoCapture(0)
    bg_init(cam)

import time
import numpy as np
from six.moves import xrange
import cv2
def bg_init(cam, mode = 1):
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
    #color_threshold = (200, 200, 200)
    color_threshold = (0, 0, 0)
    percentage_threshold = 0.9
    bg = None
    if mode==1:
        while not stabil:

            frames = frames_init(cam)
            x = frames[0].shape[0]
            y = frames[0].shape[1]
            area = x*y

            t = np.vstack(frames)
            masked = t>color_threshold
            masked = masked.astype(int)
            #masked = np.prod(masked, 2)
            #print(masked.shape, area)

            correct = np.count_nonzero(masked)
            #print(correct)

            # if the correct points in frames is bigger than required percentage 
            # we think its a proper background
            if correct/area/10 > percentage_threshold:
                stabil = True
                b = np.zeros((x,y,3))
                for a in frames:
                    b = a+b

                bg = b/len(frames)

        print('background init succeed')
        return bg

            

        

    pass

def frames_init(cam, batch_size=4, time_interval=1):
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
        _, img = cam.read()
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



def change_coordinate_player(mask_player ,img , bg2, mode=1):
    """
    change the coordinate of the player_mask if necessary
    input:
        player_mask: the mask of the player region in the bg1
        bg2: the background in the live game under mode 1
        mode: the mode of the game
    output:
        mask_player
    """
    if mode == 1:
        b_x = bg2.shape[0]
        b_y = bg2.shape[1]
        b_z = bg2.shape[2]

        x = img.shape[0]
        y = img.shape[1]
        z = img.shape[2]


        mask = np.zeros((b_x, b_y))
        img_global = np.zeros((b_x,b_y,b_z))
        mask[b_x-x:,b_y-y:] = mask_player
        img_global[b_x-x:,b_y-y:,] = img

        return mask, img_global



def change_coordinate_stone_and_collision_test(stone, bg2, mode=1):
    hit_wall = False
    bg_h = bg2.shape[0]
    bg_w = bg2.shape[1]
    
    if mode == 1:
        stone_mask,  _ = stone.get_mask()

        cv2.imwrite('./test/stone_mask1.png', stone_mask)

        print('here')
        stone_x_dist, stone_y_dist = stone.get_address()
        stone_h = stone_mask.shape[0]
        stone_w = stone_mask.shape[1]

        mask_stone_bg = np.zeros((bg_h, bg_w))
        stone_img_bg = np.zeros((bg_h, bg_w, 3))
        
        # hit the wall
        if stone_x_dist<0 or stone_y_dist<0 or stone_x_dist+stone_h>bg_h or stone_y_dist+stone_w>bg_w:
            hit_wall = True
            mask_stone_bg = None
            stone_img = None
        else:
            hit_wall = False
            mask_stone_bg[stone_x_dist:stone_x_dist+stone_h, stone_y_dist:stone_y_dist+stone_w] = stone_mask
            stone_img = stone.get_img()
            stone_img = _get_img_by_mask(stone_img,stone_mask)
            stone_img_bg[stone_x_dist:stone_x_dist+stone_h, stone_y_dist:stone_y_dist+stone_w,:] = stone_img
    return mask_stone_bg, stone_img_bg, hit_wall

        

def check_hit(mask_player_bg, stones, bg2):
    """
    check if the stone hit the player, if so, change the state of the stone
    it:
        mask_player: the mask of the player
        stones: the list of stone
    """

    bg_h = bg2.shape[0]
    bg_w = bg2.shape[1]
    for stone in stones:
        # only process the stone with the state 'live'
        if stone.get_state() != 'live':
            continue
        mask_stone_bg,stone_img, hit_wall = change_coordinate_stone_and_collision_test(stone, bg2)
        if not hit_wall:
            result = mask_player_bg*mask_stone_bg
            if np.sum(result)>15:
                stone.set_state('win')
            else:
                pass
        else:
            stone.set_state('dead')




        

def _get_img_by_mask(img, mask):
        
        r = img[:,:,0:1].reshape(img.shape[0],img.shape[1])
        g = img[:,:,1:2].reshape(img.shape[0],img.shape[1])
        b = img[:,:,2:3].reshape(img.shape[0],img.shape[1])
        
        r *= mask
        g *= mask
        b *= mask

        return np.hstack([r,g,b]).reshape(img.shape[0],img.shape[1],3)

def _delete_img_by_mask(img, mask):
    mask = (mask-1)*-1
    return _get_img_by_mask(img, mask)


def combine(img, bg2, mask_player_local, stones):
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
    def _remove_stones(stones):
        stones = [stone for stone in stones if stone.countdown != 0]

    def _inner_process(bg, img, mask):
        # img and mask are global
        bg = _delete_img_by_mask(bg, mask)
        img = _get_img_by_mask(img, mask)
        return bg+img
        
    result = bg2

    if mask_player_local is not None:
        # combine player
        player_mask, player_img = change_coordinate_player(mask_player_local, img, bg2)
        result = _inner_process(bg2, player_img, player_mask)


    # combine stone
    stone_mask = None
    stone_img = None
    for stone in stones:
        stone_mask,stone_img, hit_wall = change_coordinate_stone_and_collision_test(stone, bg2)
        if not hit_wall:
            print(stone_mask)
            cv2.imwrite('./test/stone_mask.png', stone_mask)
 
            result = _inner_process(bg2, stone_img, stone_mask)
    _remove_stones(stones)

    return result

    pass

def frames_update(cam, frames, time_delay=0.1):
    """
    update the img in the frame list
    input:
        cam: instance of the camera
        frames: frame list to store the frame
        cycle_length: frequece to update the frame output: frames """ 
    time.sleep(time_delay)
    ret_val, img = cam.read() 
    # reaching the edge. set the stage to the next and initialize other attribs
    frames.append(img)
    frames.pop(0)
    return frames



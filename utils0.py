import cv2
import numpy as np

from Stone import Stone

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
    print("--- initializing the background")
    _, img = cam.read()
    print("background size: ", img.dtype, img.shape)
    print("+++ finish initializing the background")
    return img, img

def frames_init(cam, batch_size):
    """
    init the original frame list
    input:
        cam: instance of the camera
        batch_size: the number of frame in the list
    output:
        frames: output the list of the frame
    """
    print("--- initializing the frames")
    frames = []
    for i in range(batch_size):
        _, img = cam.read()
        frames.append(img)
    print("+++ finish initializing the frames")
    return frames

def get_player_mask(img, bg):
    """
    only recognize the player under the line
    pay attention that, the return mask should be size of img. not only the part under the line
    input:
        img: the image getting from the frames
        bg: the background of the game 
    output:
        mask_player
   """
    fg = img
    rows_bg, cols_bg, channels_bg = bg.shape
    rows_fg, cols_fg, channels_fg = fg.shape
    line = int(round(0.5 * rows_bg))
    assert(cols_bg == cols_fg)
    # only check the area under the line
    bg = bg[rows_bg - line: rows_bg]
    fg = fg[rows_bg - line: rows_fg]
    # get the difference between the bg and fg
    gray_bg = cv2.cvtColor(bg, cv2.COLOR_BGR2GRAY)
    gray_fg = cv2.cvtColor(fg, cv2.COLOR_BGR2GRAY)
    gray_diff = img_sub(gray_bg, gray_fg)
    # print('line: ', line)
    # print('gray_fg: ', gray_fg)
    # print('gray_bg: ', gray_bg)
    # print('gray_diff:', gray_diff)
    ret, mask = cv2.threshold(gray_diff, 30, 255, cv2.THRESH_BINARY)
    # set the kernel for opening and closing
    kernel = np.ones((5, 5), np.uint8)
    mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, kernel)
    mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, kernel)
    # put this part of mask into the img's mask
    mask_img = np.zeros([rows_bg, cols_bg], dtype = 'uint8')
    mask_img[rows_bg - line: rows_bg] = mask
    return mask_img
def img_sub(img1, img2):
        """
        return |img1 - img2|
        """
        shape_img1 = img1.shape
        shape_img2 = img2.shape
        assert(shape_img1 == shape_img2)
        img1 = img1.reshape([-1])
        img2 = img2.reshape([-1])
        diff = np.array(map(_uint8_abs_sub, img1, img2), dtype = 'uint8')
        diff = diff.reshape(shape_img1)
        return diff

def _uint8_abs_sub(v1, v2):
        """
        return |v1 - v2|
        """
        if v1 > v2:
            return v1 - v2
        else:
            return v2 - v1


def change_coordinate(mask_player, bg, mode):
    """
    change the coordinate of the player_mask if necessary
    input:
        player_mask: the mask of the player region in the bg1
        bg: the background of the game in the mode 1
        mode: the mode of the game
    output:
        mask_player
    """
    return mask_player

def check_hit(mask_player, stones):
    """
    check if the stone hit the player, if so, change the state of the stone
    input:
        mask_player: the mask of the player
        stones: the list of stone
    """
    # direct bitwise_and the mask of stone and human
    # but should extend the mask of stone at first
    # set the mask of player as background and the mask of stone as forground
    rows_bg, cols_bg = mask_player.shape
    for stone in stones:
        # extend the mask of stone to the size of mask_player
        mask_fg = np.zeros(mask_player.shape, dtype = 'uint8')
        add_x, add_y = stone.get_address()
        rows_stone, cols_stone, _ = stone.get_size()
        mask_stone, _ = stone.get_mask()
        if add_x >= 0 and add_y >= 0 and add_x + rows_stone <= rows_bg and add_y + cols_stone <= cols_bg: # the condition here is false, only for test
            mask_fg[add_x: add_x + rows_stone, add_y: add_y + cols_stone] = mask_stone
            # use bitwise_and to get the intersection between two mask 
            intersection = cv2.bitwise_and(mask_fg, mask_player)
            if np.sum(intersection) >= 10: 
                # if the sum of intersection larger as 30, we say that the stone hit the player
                stone.set_state('win')
        else:
            # the stone run out of the boundary, set the state of the stone to dead
            if stone.get_state() == 'live':
                print "stone stay out of the image, set it to dead"
                stone.set_state('dead')

def combine(bg1, bg2, img, mask_player, stones, mode):
    """
    draw the stone on the image 
    input:
        img: the imgage getting from the frames
        bg2: the background of mode 1
        mask_player: the mask for the player
        stones: the list of the stones
        mode: the mode of the game
    output:
        img
    """
    bg = img
    for stone in stones:
        bg = combine_stone(bg, stone)
    return bg

def combine_stone(img, stone):
    bg = img
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
        if stone.get_state() == 'live':
            print "stone jump out the bound, if it is not dead, set it's state to Dead then process the next stone"
            print("address of stone: ", (add_x, add_y), "size of the stone", stone.get_size())
            print('boudary of the background:', (rows_bg, cols_bg))
            stone.set_state('dead')
    return bg

def frames_update(cam, frames, cycle_length):
    """
    update the img in the frame list
    input:
        cam: instance of the camera
        frames: frame list to store the frame
        cycle_length: frequece to update the frame
    output:
        frames
    """
    print("--- updating the frames")
    ret_val, img = cam.read() # get the current img from the camera
    if not isinstance(img, np.ndarray):
        print "img is NoneType, i also don't know why"
    # save newest batch_size frames in the frames. and try to do some preparation if necessary
    # reaching the edge. set the stage to the next and initialize other attribs
    frames.append(img)
    frames.pop(0)
    print("+++ finishing updating the frame")
    return frames



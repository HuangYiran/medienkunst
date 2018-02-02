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
    pass

def frames_init(cam, batch_size):
    """
    init the original frame list
    input:
        cam: instance of the camera
        batch_size: the number of frame in the list
    output:
        frames: output the list of the frame
    """
    pass

def get_player_mask(img, bg):
    """
    the the mask of the player rio
    input:
        img: the image getting from the frames
        bg: the background of the game 
    output:
        mask_player
    """
    pass

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
    pass

def check_hit(mask_player, stones):
    """
    check if the stone hit the player, if so, change the state of the stone
    input:
        mask_player: the mask of the player
        stones: the list of stone
    """
    pass

def combine(img, bg2, mask_player, stones, mode):
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
    pass

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
    ret_val, img = cam.read() # get the current img from the camera
    if not isinstance(img, np.ndarray):
        print "img is NoneType, i also don't know why"
        continue
    # save newest batch_size frames in the frames. and try to do some preparation if necessary
    if cnt < cycle_length:
        # update the frames until reach the edge
        cnt = cnt+1
    else:
        # reaching the edge. set the stage to the next and initialize other attribs
        frames.append(img)
        frames.pop(0)
        cnt = 0
    return frames



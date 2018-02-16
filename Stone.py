import cv2
import numpy as np

class Stone():
    def __init__(self, init_img, init_x, init_y, m_mode, init_scale = 1, init_whilr = 0, countdown = 10):
        """
        img: numpy.array, the initial image of the stone
        cor_x: the current x coordinate of the stone, left up side
        cor_y: the current y coordinate of the stone
        scale: the scale of the stone default is 1
        whirl: the whirl of the stone default is 0
        m_modes: the modes that add to the stone, e.x. Gravity
        state: the state of the stone including live, dead(when it hit the floor), win(whenn it hit the man)
        countdown: when the state of the stone changed to dead or win, start to count down. when countdown == 0, the stone will be removed from the stones list.
        """
        self.img = init_img
        self.img = cv2.resize(self.img, (100, 100))
        # mask 0 or 255
        self.mask, self.mask_inv = self._create_mask()
        # set the img to a fix size
        self.cor_x = init_x
        self.cor_y = init_y
        self.scale = init_scale
        self.whirl = init_whilr
        self.m_modes = [m_mode]
        self.state = 'live'
        self.countdown = countdown
	self.masked_img = self._calc_masked_img()
	self.bool_mask_3d = self._calc_bool_mask_3d()
	self.bool_mask_inv_3d = (self.bool_mask_3d-1)*-1

        # mask will be changed with time
        self.mask_bg = None

    def _calc_masked_img(self):
	m = self.img.shape[0]
        n = self.img.shape[1]
	r = self.img[:,:,0:1].reshape(m,n)
	g = self.img[:,:,1:2].reshape(m,n)
	b = self.img[:,:,2:3].reshape(m,n)

	r *= self.mask
	g *= self.mask
	b *= self.mask
	result = self.img
	result[:,:,0:1] = r.reshape(m,n,1)
	result[:,:,1:2] = g.reshape(m,n,1)
	result[:,:,2:3] = b.reshape(m,n,1)
	return result

    def _create_mask(self):
        img2gray = cv2.cvtColor(self.img, cv2.COLOR_BGR2GRAY)
        ret, mask_inv = cv2.threshold(img2gray, 250, 255, cv2.THRESH_BINARY) # because the backgroud of the stone white is, we use THRES_BINARY_INV
        mask = cv2.bitwise_not(mask_inv)
        return mask, mask_inv

    def _calc_bool_mask_3d(self):
	t = self.mask/255
	t = np.repeat(t, 3).reshape(100,100,3)
	return t

    def _hit_wall(self, h,w,x,y):
	if x<0 or y<0 or x+100>h or y+100>w:
	    return True
	else:
	    return False

    def draw_in_bg(self, bg2, player_mask):
	self.run()
	h,w,_ = bg2.shape
	x,y = self.get_address()
	if self._hit_wall(h,w,y,x):
	    self.state = 'dead'
	    
	else:
	    
            self.check_hit(player_mask, bg2)
	    bg2[y:y+100,x:x+100,:] *= self.bool_mask_inv_3d
	    bg2[y:y+100,x:x+100,:] += self.masked_img
	    
	return bg2

    def _get_mask_bg(self, bg2):
        # calc mask of stone in the backgroud
        h,w,_ = bg2.shape
        x,y = self.get_address()
        mask_bg = np.zeros((h,w))
        #print(x,y)
        #print(self.mask.shape,mask_bg[y:y+100,x:x+100].shape )
        mask_bg[y:y+100,x:x+100] = self.mask/255
        return mask_bg
        
    def check_hit(self, player_mask, bg2):
        # check whether stone hits the player
        mask_bg = self._get_mask_bg(bg2)
        mask_sum = mask_bg + player_mask
        # calc the same area between stone mask and player mask
        s = np.sum(mask_sum>1)
        if s>15:
            self.state='win'
            return True
        else:
            return False


    def get_img(self):
        return self.img

    def get_mask(self):
        return self.mask, self.mask_inv

    def set_mask(mask, mask_inv):
        self.mask = mask
        self.mask_inv = mask_inv

    def get_size(self):
        # rows, cols, channels
        return self.img.shape

    def get_address(self):
        """
        the real address of the stone can be float, 
        but when you try to draw the stone on the image, we need a int value, so we create this function 
        if you want to get the real address, you can use get_real_address() function
        """
        # (x, y) : (cor_x, cor_y)
        return int(round(self.cor_x)), int(round(self.cor_y))

    def get_real_address(self):
        """
        return the real address of the stone, this value can be float
        """
        return cor_x, cor_y

    def add_mode(self, mode):
        self.m_modes.append(mode)

    def set_scale(self, scale):
        self.scale = scale

    def get_scale(self):
        return self.scale

    def set_whirl(self, whirl):
        self.whirl = whirl

    def get_whirl(self):
        return self.whirl

    def set_state(self, state):
        self.state = state
        if state == 'win':
            self.img = cv2.imread("./bilds/win.jpg") # set the img to a winner sign
            self.img = cv2.resize(self.img, (100, 100))
        elif state == 'dead':
            # self.img = 'dead'  set the img to a loser sign
            print "++++++++++++++++dead++++++++++"
            self.img = cv2.imread("./bilds/dead.jpg")
            self.img = cv2.resize(self.img, (100, 100))
            self.cor_x = self.cor_x - 20
        self.mask, self.mask_inv = self._create_mask()

    def get_state(self):
        return self.state

    def run(self):
        if self.state == 'live':
            for mode in self.m_modes:
                mode.run(self)
        else:
            self.countdown = self.countdown - 1

import cv2

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
        self.img = cv2.resize(self.img, 100, 100)
        self.mask, self.mask_inv = self._create_mask()
        # set the img to a fix size
        self.cor_x = init_x
        self.cor_y = init_y
        self.scale = init_scale
        self.whirl = init_whilr
        self.m_modes = [m_mode]
        self.state = 'live'
        self.countdown = countdown

    def _create_mask(self):
        img2gray = cv2.cvtColor(self.img, cv2.COLOR_BGR2GRAY)
        ret, mask = cv2.threshold(img2gray, 10, 240, cv2.THRESH_BINARY)
        mask_inv = cv2.bitwise_not(mask)
        return mask, mask_inv

    def get_img(self):
        return self.img

    def get_mask(self):
        return self.mask, self.mask_inv

    def get_size(self):
        # rows, cols, channels
        return self.img.shape

    def get_address(self):
        # (x, y) : (cor_x, cor_y)
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
            self.img = 'win' # set the img to a winner sign
        elif state == 'dead':
            self.img = 'dead' # set the img to a loser sign

    def get_state(self):
        return self.state

    def run(self):
        if self.state == 'live':
            for mode in self.m_modes:
                mode.run(self)
        else:
            self.countdown = self.countdown - 1

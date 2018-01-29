class stone():
    def __init__(self, init_img, init_x, init_y, m_mode, init_scale = 1, init_whilr = 0, countdown = 10):
        """
        img: the initial image of the stone
        cor_x: the current x coordinate of the stone
        cor_y: the current y coordinate of the stone
        scale: the scale of the stone default is 1
        whirl: the whirl of the stone default is 0
        m_modes: the modes that add to the stone, e.x. Gravity
        state: the state of the stone including live, dead(when it hit the floor), win(whenn it hit the man)
        countdown: when the state of the stone changed to dead or win, start to count down. when countdown == 0, the stone will be removed from the stones list.
        """
        self.img = init_img
        self.cor_x = init_x
        self.cor_y = init_y
        self.scale = init_scale
        self.whirl = init_whilr
        self.m_modes = [m_mode]
        self.state = 'live'
        self.countdown = countdown

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
        return 

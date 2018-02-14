import numpy as np


class Player:
    def __init__(self, bg2, img):

        """
        input:
        img_bg: from Dodger class get the background in image
        bg is extracted background from camera
        bg2 is self sat background
        """
        self.mask = None
        self.bg2_y, self.bg2_x, _ = bg2.shape
        self.img_y, self.img_x, _ = img.shape
        self.x_ratio = 1.0*self.bg2_x/self.img_x
        self.y_ratio = 1.0*self.bg2_y/self.img_y


    def _get_all_mask(self, img, bg):
        threshold = (40,40,40)
        diff = img-bg
        diff = np.power(diff, 2)
        mask = diff>threshold
        mask = np.prod(mask, axis=2)
        return mask

    def _select_player_mask(self, mask):
        # TODO select out player
        self.mask = mask
        return self.mask

    def _get_player_pose_img(self, mask):
        # TODO check argmax
        x = np.argmax(mask, axis=1)
        y = np.argmax(mask, axis=0)
        self.player_img_pose = (x, y)

    def _get_img(self, img):
        x, y = self.player_img_pose
        print(self.player_img_pose)
        return img[y:, x:, :]

    def _get_img_pose(self):
        # img pose in bg2
        x, y = self.player_img_pose

        img_x_bg = x*self.x_ratio
        img_y_bg = y
        return img_x_bg, img_y_bg

    def draw_bg(self, bg, bg2, img):
        mask = self._get_all_mask(img, bg)
        mask = self._select_player_mask(mask)
        self._get_player_pose_img(mask)
        processed_img = self._get_img(img)
        h, w = processed_img.shape
        x, y = self._get_img_pose()
        bg2 = bg2[y:y+w, x:x+h,:]
        return bg

    def get_mask(self, img=None, bg=None):
        if self.mask is not None:
            return self.mask
        else:
            mask = self._get_all_mask(img, bg)
            return self._select_player_mask(mask)



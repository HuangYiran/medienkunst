import numpy as np
import cv2
from six.moves import xrange


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
        self.x_ratio = (1.0*self.bg2_x/self.img_x-1)

        self.y_ratio = 1.0*self.bg2_y/self.img_y
	self.center = None
	self.real_center = None
	self.img_pose = None


    def _get_all_mask(self, img, bg):
        threshold = (3000,3000,3000)
	#cv2.imwrite('./test/t_img.png', img)
	#cv2.imwrite('./test/t_bg.png', bg)
        diff = 1.0*img-1.0*bg
	
	#cv2.imwrite('./test/t_diff.png', diff)
        diff = np.power(diff, 2)
	#print(np.max(diff))
        mask = diff>threshold
	m, n, _ = mask.shape
	t1 = mask[:,:,0:1]
	t2 = mask[:,:,1:2]
	t3 = mask[:,:,2:3]
	mask = t1+t2+t3
	mask = ((mask>0).reshape(m,n)*255).astype('uint8')
	mask = cv2.blur(mask, (4,4))
	#mask = cv2.blur(mask, (2,2))
	mask = mask>150
	#cv2.imwrite('./test/t_mask.png', mask*255)
	mask = self._get_mask_in_box(mask)
	#print(np.min(diff))
        return mask

    def _get_mask_in_box(self, mask, box_l=5, threshold = 20):
	h, w = mask.shape
	
	s = None
	#print(np.sum(mask))
	for i in xrange(box_l):
	    t = mask[i::box_l, :].astype(int)

 	    if s is None:
		s = t
	    else:
		s += t
	st = s
	s = None
	for i in xrange(box_l):
	    t = st[:, i::box_l]
	    if s is None:
		s = t
	    else:
		s += t
	#print(np.max(s))
	s = s>threshold
	
	s = np.repeat(s, box_l, axis=1)
	s = np.repeat(s, box_l, axis=0)
	
	
	#return sum_h*sum_w*mask
	
	#cv2.imwrite('./test/t_box.png', (s*255).astype('uint8'))
	return s*mask
	

    def _select_player_mask(self, mask, threshold=2):
        # TODO select out player
	"""	
	mask = (mask*255).astype('uint8')
	_, contours, _ = cv2.findContours(mask, cv2.RETR_TREE,cv2.CHAIN_APPROX_SIMPLE)
	t = 0
	t_mask = None
	for contour in contours:
	    x,y,w,h = cv2.boundingRect(contour)
	    if t<w*h:
		t = w*h
		t_mask = mask[y:y+h, x:x+w]
	

	
	print(mask.shape)
	h,w = mask.shape
	sum_h = np.sum(mask, axis=1)
	sum_w = np.sum(mask, axis=0)
	top = np.argmax(sum_h)
	left = np.argmax(sum_w)
	bottom = h-np.argmax(sum_h[::-1])
	right = w-np.argmax(sum_w[::-1])
	print(top, left,bottom, right)
	t = mask[top:bottom, left:right]
	
	# print(sum_h.shape)
	sum_h = (sum_h>threshold).reshape(h,1)
	sum_w = (sum_w>threshold).reshape(1,w)

	sum_h = np.repeat(sum_h,w,axis=1)
	sum_w = np.repeat(sum_w,h,axis=0)
	t = sum_h*sum_w
	"""
	#print(t_mask.shape)
	cv2.imwrite('./test/t_box.png', mask*255)
	
        self.mask = mask
        return self.mask

    def _fill_out_mask(self, mask, fabric_r=20, fabric_c=20, rect=(150,150)):
	
	if self.real_center is None:
	    return mask
	x, y = self.real_center
	rx, ry = rect
	t = mask[y-ry:y+ry,x-rx:x+rx].copy()
	h,w = t.shape
	
	l = fabric_r*2+1
	n_row = int(h/l)-1
	n_column = int(w/l)-1
	
	
	# row
	for i in xrange(l):
	    t1 = None
	    t2 = None
	    # calc sum of left side and sum of right side 
	    for j in xrange(fabric_r-1):
		if t1 is None:
		    t1 = t[i+j::l,:]
		    t2 = t[i+j+fabric_r::l,:]
		    t1 = t1[:n_row,:]
		    t2 = t2[:n_row,:]
		else:
		    t1 += t[i+j::l,:][:n_row,:]
		    t2 += t[i+j+fabric_r::l,:][:n_row,:]
		    
	    t[i+fabric_r::l,:][:n_row,:] = t1*t2
	t += mask[y-ry:y+ry,x-rx:x+rx]
	t = (t>0)
	
	# column
	l = fabric_r*2+1
	for i in xrange(l):
	    t1 = None
	    t2 = None
	    # calc sum of left side and sum of right side 
	    for j in xrange(fabric_c-1):
		if t1 is None:
		    t1 = t[:, i+j::l]
		    t2 = t[:, i+j+fabric_c::l]
		    t1 = t1[:, :n_column]
		    t2 = t2[:, :n_column]
		else:
		    t1 += t[:, i+j::l][:, :n_column]
		    t2 += t[:, i+j+fabric_c::l][:, :n_column]
		    
	    t[:, i+fabric_c::l][:, :n_column] = t1*t2
	t += mask[y-ry:y+ry,x-rx:x+rx]
	t = (t>0)
	mask[y-ry:y+ry,x-rx:x+rx] = t
	self.mask = mask
	return mask


    def _get_player_pose_img(self, mask, theta=0.3):
        # TODO check argmax
	sum_h = np.sum(mask, axis=1)
	sum_w = np.sum(mask, axis=0)
        x = np.argmax(sum_w)
        y = np.argmax(sum_h)
	self.real_center = (x,y)
	if self.center is None:
	    self.center = (x,y)
	else:
	    p_x, _ = self.center
	    x = theta*x+(1-theta)*p_x
        self.player_img_pose = (x, y)

    def _get_img(self, img, mask):
        # return the whole img
	a,b = mask.shape
	m = np.repeat(mask,3).reshape(a,b,3)
        #x, y = self.player_img_pose
        #print(self.player_img_pose)
	nag_m = (m-1)*-1
        return img*m, nag_m

    def _get_img_pose(self):
        # img pose in bg2
        x, y = self.player_img_pose
	
        img_x_bg = x*self.x_ratio
	if img_x_bg > (self.bg2_x-self.img_x):
	    img_x_bg = self.bg2_x-self.img_x
        img_y_bg = self.bg2_y-self.img_y
	#print self.bg2_y,self.img_y

	self.img_pose = (int(img_x_bg), int(img_y_bg))
        print(x,y)
        print(self.img_pose)
        return img_x_bg, img_y_bg

    def draw_bg(self, bg, bg2, img):
        mask = self._get_all_mask(img, bg)
        mask = self._select_player_mask(mask)
	#mask = self._fill_out_mask(mask)
	#mask = self._fill_out_mask(mask)
	#self.mask = self._fill_out_mask(mask.T).T
	#mask = self.mask
	cv2.imwrite('./test/fill_out.png', mask*255)
        self._get_player_pose_img(mask)
        processed_img, nag_mask = self._get_img(img, mask)
        h, w, _	 = processed_img.shape
        x, y = self._get_img_pose()
        #bg2[y:y+w, x:x+h,:] = processed_img
	#print nag_mask.shape, bg2[y:y+h, x:x+w,:].shape
	
	bg2[y:y+h, x:x+w,:] *= nag_mask
	bg2[y:y+h, x:x+w,:] += processed_img
        return bg2

    def get_mask(self, img=None, bg=None):
        if self.mask is not None:
            return self.mask
        else:
            mask = self._get_all_mask(img, bg)
            mask = self._select_player_mask(mask)
	    #mask = self._fill_out_mask(mask)
	    #self.mask = self._fill_out_mask(mask.T).T
	    mask = self.mask
	    return mask
    def get_global_mask(self, bg2, mask):
	if self.img_pose is None:
	    return None
	else:
	    m,n,_ = bg2.shape
	    h,w = mask.shape
	    gm = np.zeros((m,n))
	    x,y = self.img_pose
	    gm[y:y+h, x:x+w] = mask
	    return gm

	    
    def _set_player_pose(self, x, y):
        self.player_img_pose = (x,y)


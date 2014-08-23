#!/usr/bin/python


class CameraBotConfig:
	
	DELAY_VALUES = [.5,1,2,3,4,5,6,7,8,9,10,15,20,30,40,50,60,90,120,150,300,600,1200,3600]
	MODE_TYPES = ['TL','ST','TLS']
	CAMERA_TYPES = ['INT','EXT']
	RESOLUTION_LIST = ['0.3MP','0.8MP','1.2MP','1.9MP','3MP','3.8MP','4MP','5MP']
	IMAGE_QUALITY_VALUES = [10,20,30,40,50,60,70,80,90,100]

	RESOLUTION_MAP = {
		'0.3MP':{'w':640, 'h':480},
		'0.8MP':{'w':1024,'h':768},
		'1.2MP':{'w':1280,'h':960},
		'1.9MP':{'w':1600,'h':1200},
		'3MP'  :{'w':2016,'h':1512},
		'3.8MP':{'w':2400,'h':1600},
		'4MP'  :{'w':2304,'h':1728},
		'5MP'  :{'w':2592,'h':1944}
		}
	
	tlDelayIdx = 10
	resolutionIdx = 7
	modeIdx = 0
	cameraIdx = 0
	imgQualityIdx = 7

	def __init__(self, inTlDelayIdx=10, 
		inResolutionIdx=7,inModeIdx=0,
		inCameraIdx=0,inImgQualityIdx=7):
		"""Config init"""
		self.tlDelayIdx = inTlDelayIdx
		self.resolutionIdx = inResolutionIdx
		self.modeIdx = inModeIdx
		self.cameraIdx = inCameraIdx
		self.imgQualityIdx = inImgQualityIdx

	def get_cur_delay(self):
		return self.DELAY_VALUES[self.tlDelayIdx]

	def get_cur_img_height(self):
		return self.RESOLUTION_MAP[self.get_cur_resolution()]['h']

	def get_cur_img_width(self):
		return self.RESOLUTION_MAP[self.get_cur_resolution()]['w']

	def get_cur_mode(self):
		return self.MODE_TYPES[self.modeIdx]

	def get_cur_camera(self):
		return self.CAMERA_TYPES[self.cameraIdx]

	def get_cur_quality(self):
		return self.IMAGE_QUALITY_VALUES[self.imgQualityIdx]

	def get_cur_resolution(self):
		return self.RESOLUTION_LIST[self.resolutionIdx]



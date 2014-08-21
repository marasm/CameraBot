#!/usr/bin/python

class CameraBotConfig:
	tlDelayIdx = 10
	resolutionIdx = 4
	modeIdx = 0
	cameraIdx = 0
	imgQualityIdx = 7

	def __init__(self, inTlDelayIdx=10, 
		inResolutionIdx=4,inModeIdx=0,
		inCameraIdx=0,inImgQualityIdx=7):
		"""Config init"""
		self.tlDelayIdx = inTlDelayIdx
		self.resolutionIdx = inResolutionIdx
		self.modeIdx = inModeIdx
		self.cameraIdx = inCameraIdx
		self.imgQualityIdx = inImgQualityIdx


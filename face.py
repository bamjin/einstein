#!/usr/bin/python3

import sys
import os
import time
import telepot
import json
import requests
import atexit
import re
import random
import string
import operator
import cv2
import matplotlib
import numpy as np
import urllib.request
import matplotlib.pyplot as plt

from urllib import parse
from apscheduler.schedulers.background import BackgroundScheduler
from telepot.delegate import per_chat_id, create_open, pave_event_space



CONFIG_FILE = 'setting.json'

class einstein(telepot.helper.ChatHandler):

	GREETING = "사진을 한장씩 보내주세요 :-)"

	global scheduler

	def __init__(self, *args, **kwargs):
		super(einstein, self).__init__(*args, **kwargs)

	def open(self, initial_msg, seed):
		self.sender.sendMessage(self.GREETING)

	def emotion(self):
		# Load raw image file into memory
		pathToFileInDisk = './pic/file.jpg'
		with open( pathToFileInDisk , 'rb' ) as f:
		    data = f.read()

		headers = dict()
		headers['Ocp-Apim-Subscription-Key'] = _key
		headers['Content-Type'] = 'application/octet-stream'

		json = None
		params = None
		faces = list()
		result = processRequest( json, data, headers, params )
		if result is not None:
			# Load the original image from disk
			data8uint = np.fromstring( data, np.uint8 ) # Convert string to an unsigned int array
			img = cv2.cvtColor( cv2.imdecode( data8uint, cv2.IMREAD_COLOR ), cv2.COLOR_BGR2RGB )
			if len(result) < 1:
				self.sender.sendMessage("얼굴이 검출되지 않았습니다.")
			else:
				renderResultOnImage( result, img )
				matplotlib.image.imsave('./pic/face.png', img)
				self.sender.sendPhoto(open('./pic/face.png', 'rb'))
				result.sort(key=lambda x: x["faceRectangle"]["left"])
				for re in result:
					anger = float(re['scores']['anger']) * 100
					disgust = float(re['scores']['disgust']) * 100
					fear = float(re['scores']['fear']) * 100
					sadness = float(re['scores']['sadness']) * 100
					contempt = float(re['scores']['contempt']) * 100
					neutral = float(re['scores']['neutral']) * 100
					surprise = float(re['scores']['surprise']) * 100
					happiness = float(re['scores']['happiness']) * 100

					if len(result) > 1:
						key = result.index(re) + 1
						message = ("%d번 얼굴 \n화: %f %%\n혐오: %f %%\n두려움: %f %%\n슬픔: %f %%\n경멸: %f %%\n중립: %f %%\n놀라움: %f %%\n행복: %f%%"
												% (key, anger, disgust, fear, sadness, contempt, neutral, surprise, happiness))
						faces.append(message)
					else:
						self.sender.sendMessage("화: %f %%\n혐오: %f %%\n두려움: %f %%\n슬픔: %f %%\n경멸: %f %%\n중립: %f %%\n놀라움: %f %%\n행복: %f%%"
											% (anger, disgust, fear, sadness, contempt, neutral, surprise, happiness))

				self.sender.sendMessage("\n\n".join(faces))

	def on_message(self, msg):
		content_type, chat_type, chat_id= telepot.glance(msg)

		if content_type is 'text':
			self.sender.sendMessage("사진'만' 한장 보내주세요")
			return

		if content_type is 'photo':
			self.sender.sendMessage("조금 기다려주세요....")
			bot.download_file(msg['photo'][-1]['file_id'], './pic/file.jpg')
			self.emotion()
			return

	def on_close(self, exception):
		pass

def processRequest( json, data, headers, params ):

	"""
	Helper function to process the request to Project Oxford

	Parameters:
	json: Used when processing images from its URL. See API Documentation
	data: Used when processing image read from disk. See API Documentation
	headers: Used to pass the key information and the data type request
	"""

	retries = 0
	result = None

	while True:

		response = requests.request( 'post', _url, json = json, data = data, headers = headers, params = params )

		if response.status_code == 429:

			print( "Message: %s" % ( response.json()['error']['message'] ) )

			if retries <= _maxNumRetries:
				time.sleep(1)
				retries += 1
				continue
			else:
				print( 'Error: failed after retrying!' )
				break

		elif response.status_code == 200 or response.status_code == 201:

			if 'content-length' in response.headers and int(response.headers['content-length']) == 0:
				result = None
			elif 'content-type' in response.headers and isinstance(response.headers['content-type'], str):
				if 'application/json' in response.headers['content-type'].lower():
					result = response.json() if response.content else None
				elif 'image' in response.headers['content-type'].lower():
					result = response.content
		else:
			print( "Error code: %d" % ( response.status_code ) )
			print( "Message: %s" % ( response.json()['error']['message'] ) )

		break

	return result

def renderResultOnImage( result, img ):

	"""Display the obtained results onto the input image"""

	result.sort(key=lambda x: x["faceRectangle"]["left"])
	for currFace in result:
		faceRectangle = currFace['faceRectangle']
		cv2.rectangle( img,(faceRectangle['left'],faceRectangle['top']),
			(faceRectangle['left']+faceRectangle['width'], faceRectangle['top'] + faceRectangle['height']),
			color = (255,0,0), thickness = 5 )


	for currFace in result:
		faceRectangle = currFace['faceRectangle']
		currEmotion = max(currFace['scores'].items(), key=operator.itemgetter(1))[0]
		num = result.index(currFace) + 1


		textToWrite = "%d: %s" % ( num, currEmotion )
		cv2.putText( img, textToWrite, (faceRectangle['left'],faceRectangle['top']-10), cv2.FONT_HERSHEY_SIMPLEX, 1, (255,0,0), 2 )

def parseConfig(filename):
	f = open(filename, 'r')
	js = json.loads(f.read())
	f.close()
	return js

def getConfig(config):
	global TOKEN
	global _url
	global _key
	global _maxNumRetries

	_url = 'https://westus.api.cognitive.microsoft.com/emotion/v1.0/recognize'
	_maxNumRetries = 10
	TOKEN = config['common']['token']
	_key = config['common']['key']


config = parseConfig(CONFIG_FILE)

if not bool(config):
	print("Err: Setting file is not found")
	exit()

getConfig(config)
scheduler = BackgroundScheduler()
scheduler.start()
bot = telepot.DelegatorBot(TOKEN, [
	pave_event_space()
	(per_chat_id(), create_open, einstein, timeout=120),
])
bot.message_loop(run_forever='Listening...')

#!/usr/bin/env python3
# This Python file uses the following encoding: utf-8

import requests
import time
from html.parser import HTMLParser
import os
import json

# https://cn.bing.com/az/hprichbg/rb/GreatSaltLake_ZH-CN12553220159_1920x1080.jpg
# https://cn.bing.com/az/hprichbg/rb/GreatSaltLake_ZH-CN12553220159_768x1366.jpg

os.system('rm -fr imageUrl/*')
os.system('rm -fr web/*')

images = []
imagesObj = []

class MyHtmlParser(HTMLParser):

	"""初始化"""
	def __init__(self, fileName):
		HTMLParser.__init__(self)
		# self.f = open(fileName, 'w')

	def __del__(self):
		# self.f.close()
		pass

	def handle_starttag(self, tag, attrs):
		print('start tag: ', tag)
		print('attrs: ', attrs)
		for attr in attrs:
			print('		attr: ', attr)
			print('src: ', attrs[0])
		if len(attrs)>0:
			if attrs[0][0] == 'src' and 'jpg' in attrs[0][1]:
				print("attrs[0][0]: ", attrs[0][0])
				images.append(attrs[0])
				self.src=attrs[0][0]
				self.jpg=attrs[0][1]

	def handle_endtag(self, tag):
		print('end tag: ', tag)

	def handle_data(self, dataCount):
		print('data: ', dataCount)
		if '(2017' in dataCount or '(2016' in dataCount:
			self.data=dataCount[-10:]
			oneDay=OneDay(dataCount, self.jpg, self.data)
			imagesObj.append(oneDay)
			print('oneDay:', json.dumps(oneDay, default=oneDay2dict))

	def handle_comment(self, comment):
		print('comment: ', comment)

	def handle_charref(self, charref):
		print('charref: ', charref)

	def handle_decl(self, decl):
		print('decl: ', decl)

class OneDay(json.JSONEncoder):
	"""Image Class"""
	def __init__(self, s, j, d):
		self.src=s
		self.jpg=j
		self.data=d

def oneDay2dict(oneDay):
    return {
        'alt': oneDay.src,
        'jpg': oneDay.jpg[0:-8],
        'data': oneDay.data[1:9]
    }

def oneDay2dict2(oneDay):
    return {
        'alt': oneDay.src,
        'jpg': oneDay.jpg,
        'data': oneDay.data
    }

def getImage():
	for pageNum in range(1, 51):
		weburl = "http://bing.plmeizi.com/?page=" + str(pageNum)
		page = requests.get(weburl)
		my = MyHtmlParser('web/' + str(pageNum) + '.txt');
		print(page.text)
		my.feed(page.text)
		with open('imageUrl/temp_' + str(pageNum) + '.txt', 'w') as f:
			# f.write(str(images))
			pass
		print('-------------------')
		# print(images)
		print('-------------------')
		# images=[]
		# img_name = '/Users/ren/Desktop/GitHub/python/web/' + str(pageNum) + '.txt'
		# with open(img_name,'wb') as f:
		# 	f.write(page.content)
		jsonStr = json.dumps(list(imagesObj), default=oneDay2dict)
		with open('all.json', 'w') as fJ:
			fJ.write(jsonStr)
		print('download successful: ' + str(pageNum))

def downloadImage():
	with open('all.json', 'r') as f:
		imagesObj=json.load(f)
	print(imagesObj)
	for imageObjTemp in imagesObj:
		print(imageObjTemp['jpg'])
		imgUrl = imageObjTemp['jpg']
		imageWebUrl = imgUrl
		imgUrl = imgUrl.replace('http://bimgs.plmeizi.com/images/bing/2017/', '').replace('http://bimgs.plmeizi.com/images/bing/2016/', '').replace('http://s.cn.bing.net/az/hprichbg/rb/', '')
		img = requests.get(imageWebUrl)
		with open('write/' + imgUrl, 'wb') as f:
			f.write(img.content)

def getNowTime():
    return int(time.strftime("%Y%m%d",time.localtime(time.time())))

def getImageFromBing():
	with open('all.json', 'r') as f:
		imagesObj=json.load(f)
	# print(imagesObj[0]['data'])
	imageData = int(imagesObj[0]['data'])
	if getNowTime() == imageData:
		print('today bing image has load')
		return
	# print(imageData)
	url = 'http://www.bing.com/HPImageArchive.aspx?format=js&idx=0&n=10&mkt=en-US'
	imagesJson = requests.get(url)
	# print(imagesJson.text)
	jsonObj= json.loads(str(imagesJson.text))
	# print(jsonObj)
	position = 0
	for bingImageObj in jsonObj['images']:
		# print(bingImageObj)
		if int(bingImageObj['enddate']) > imageData:
			oneDay = OneDay(bingImageObj['copyright'] + ' ('+ bingImageObj['enddate'] +')', 'http://www.bing.com' + bingImageObj['url'], bingImageObj['enddate'])
			img = requests.get('http://www.bing.com' + bingImageObj['url'])
			imgUrl = bingImageObj['url'].replace('th?id=OHR.', '').replace('&rf=LaDigue_1920x1080.jpg&pid=hp', '').replace('&rf=NorthMale_1920x1080.jpg&pid=hp', '').replace('/az/hprichbg/rb/', '')
			with open('images/' + imgUrl, 'wb') as f:
				f.write(img.content)
			imagesObj.insert(position, oneDay)
			position = position + 1
			jsonStr = json.dumps(list(imagesObj), default=oneDay2dict2)
			with open('all.json', 'w') as fJ:
				fJ.write(jsonStr)
	os.system('git add .')
	os.system('git commit -m "'+str(getNowTime())+'"')
	os.system('git push origin master')

if __name__ == "__main__":
    # getImage()
	# downloadImage()
	getImageFromBing()

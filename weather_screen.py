#!/usr/bin/env python2.5
# -*- coding: utf-8 -*-
__author__ = "Soeren Apel (abraxa@dar-clan.de), Frank Gau (fgau@gau-net.de), Thomas Gstaedner (thomas (a) gstaedtner (.) net)"
__version__ = "prototype"
__copyright__ = "Copyright (c) 2008"
__license__ = "GPL3"

TEMP_UNIT = 'c'

WEATHER_URL = 'http://xml.weather.yahoo.com/forecastrss?p=%s&u=%s'
WEATHER_NS = 'http://xml.weather.yahoo.com/ns/rss/1.0'

from epydial import *
import urllib
from xml.dom import minidom

class WeatherScreen():
	def register_pyneo_callbacks(self):
		pass

	def __init__(self, screen_manager):
		self.zip_code = ['GMXX0007', 'GMXX0028', 'GMXX0049', 'GMXX0063', 'GMXX0096', 'GMXX0040']
		self.state_type = self.zip_code[0]
		self.buttons = {}
		self.contents = {}
		self.canvas = screen_manager.get_evas()

		self.bg = evas.Image(self.canvas, pos=(0, 0), size=(WIDTH, HEIGHT), file=PyneoController.set_bg_image)
		self.bg.fill = 0, 0, WIDTH, HEIGHT
		self.bg.layer = 99

		self.headline = evas.Text(self.canvas, text="weather", font=("Sans:style=Bold,Edje-Vera", 60), color="#808080")
		self.headline.layer = 99
		self.headline.pos = ((480-self.headline.horiz_advance)/2, 25)

		self.subheadline = evas.Text(self.canvas, font=("Sans:style=Bold,Edje-Vera", 30), color="#808080")
		self.subheadline.layer = 99

		for pos, text in enumerate(["back", "previous", "next"]):
			self.buttons[text] = self.init_button(text, (pos+1)*16+pos*100, 524, 100, 100)

		for pos, text in enumerate(["current", "forecast"]):
			for i, row in enumerate(["pix", "date", "temp", "condition"]):
				self.contents[text, row] = self.init_content(row, text, 10, (pos+1)*150)

		self.weather_for_zip(self.state_type, TEMP_UNIT)

	def init_content(self, row, name, x, y):
		if row == 'pix':
			weather_pix = evas.Image(self.canvas, pos=(340,y), size=(120,120))
			weather_pix.fill = 0, 0, 120, 120
			weather_pix.layer = 99
			return weather_pix
		if row == 'date':
			date = evas.Text(self.canvas, font=("Sans:style=Edje-Vera", 18), color="#808080")
			date.pos = (10, y+10)
			date.layer = 99
			return date
		if row == 'temp':
			high_low = evas.Text(self.canvas, font=("Sans:style=Edje-Vera", 18), color="#808080")
			high_low.pos = (10, y+30)
			high_low.layer = 99
			return high_low
		elif row == 'condition':
			condition = evas.Text(self.canvas, font=("Sans:style=Edje-Vera", 18), color="#808080")
			condition.pos = (10, y+50)
			condition.layer = 99
			return condition

	def init_button(self, name, x, y, dx, dy):
		def button_callback(source, event):
			if name == 'back':
				PyneoController.show_dialer_screen()
			elif name == 'next':
				states_avail = self.zip_code
				self.state_type = states_avail[(states_avail.index(self.state_type)+1)%len(states_avail)]
				self.weather_for_zip(self.state_type, TEMP_UNIT)
			elif name == 'previous':
				states_avail = self.zip_code
				self.state_type = states_avail[(states_avail.index(self.state_type)-1)%len(states_avail)]
				self.weather_for_zip(self.state_type, TEMP_UNIT)
			print '--- ', name
		button = evas.Image(self.canvas, pos=(x,y), size=(dx,dy), file="/usr/share/epydial/data/themes_data/blackwhite/images/%s.png" % name)
		button.fill = 0, 0, dx, dy
		button.layer = 99
		button.on_mouse_up_add(button_callback)
		return button

	def weather_for_zip(self, zip_code, unit):
		url = WEATHER_URL % (zip_code, unit)
		def parse(content):
			dom = minidom.parse(urllib.urlopen(url))
			forecasts = []
			for node in dom.getElementsByTagNameNS(WEATHER_NS, 'forecast'):
				forecasts.append({
					'date': node.getAttribute('date'),
					'low': node.getAttribute('low'),
					'high': node.getAttribute('high'),
					'condition': node.getAttribute('text'),
					'code': node.getAttribute('code'),
				})
			ycondition = dom.getElementsByTagNameNS(WEATHER_NS, 'condition')[0]

			self.subheadline.text = dom.getElementsByTagName('title')[0].firstChild.data[17:]
			self.subheadline.pos = ((480-self.subheadline.horiz_advance)/2, 110)
			self.contents['current', 'pix'].file_set('%s%s.png' % (PIX_WEATHER_FILE_PATH, ycondition.getAttribute('code')))
			self.contents['current', 'pix'].fill = 0, 0, 120, 120
			self.contents['current', 'date'].text = ('date: %s' % ycondition.getAttribute('date'))
			self.contents['current', 'temp'].text = ('current temp: %s' % ycondition.getAttribute('temp'))
			self.contents['current', 'condition'].text = ('condition: %s' % ycondition.getAttribute('text'))
			self.contents['forecast', 'pix'].file_set('%s%s.png' % (PIX_WEATHER_FILE_PATH, forecasts[1]['code']))
			self.contents['forecast', 'pix'].fill = 0, 0, 120, 120
			self.contents['forecast', 'date'].text = ('date: %s' % (forecasts[1]['date']))
			self.contents['forecast', 'temp'].text = ('temp low/high: %s/%s' % (forecasts[1]['low'], forecasts[1]['high']))
			self.contents['forecast', 'condition'].text = ('condition: %s' % (forecasts[1]['condition']))
		PyneoController.urlread(url, parse)

	def show(self):
		self.bg.show()
		self.headline.show()
		self.subheadline.show()

		for pos, text in enumerate(["back", "previous", "next"]):
			self.buttons[text].show()

		for pos, text in enumerate(["current", "forecast"]):
			for i, row in enumerate(["pix", "date", "temp", "condition"]):
				self.contents[text, row].show()

	def hide(self):
		self.bg.hide()
		self.headline.hide()
		self.subheadline.hide()

		for pos, text in enumerate(["back", "previous", "next"]):
			self.buttons[text].hide()

		for pos, text in enumerate(["current", "forecast"]):
			for i, row in enumerate(["pix", "date", "temp", "condition"]):
				self.contents[text, row].hide()

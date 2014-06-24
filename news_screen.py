#!/usr/bin/env python2.5
# -*- coding: utf-8 -*-
from __future__ import with_statement
__author__ = "F. Gau <fgau@pyneo.org>"
__version__ = "prototype"
__copyright__ = "Copyright (c) 2009"
__license__ = "GPL3"

from epydial import *

STYLE = """
DEFAULT='font=Sans font_size=18 align=left color=#808080 wrap=word valign=top'
h1='+ font_size=38 font=Bookman'
/h1='- \\n \\n'
p='+ '
/p='- \\n \\n'
br='\\n'
red='+ color=#660000'
/red='-'
center='+ align=center'
/center='-'
big='+ font_size=40'
/big='-'
"""

class NewsScreen():

	def register_pyneo_callbacks(self):
		PyneoController.register_callback("show_news", self.on_show_news)

	def __init__(self, screen_manager):
		self.FONT_COLOR = PyneoController.set_font_color
		self.buttons = {}
		self.keys = {}
		self.canvas = screen_manager.get_evas()

		self.bg = evas.Image(self.canvas, pos=(0, 0), size=(WIDTH, HEIGHT), file=PyneoController.set_bg_image)
		self.bg.fill = 0, 0, WIDTH, HEIGHT
		self.bg.layer = 99

		self.headline = evas.Text(self.canvas, text="news", font=("Sans:style=Bold,Edje-Vera", 60), color=self.FONT_COLOR)
		self.headline.layer = 99
		self.headline.pos = ((WIDTH-self.headline.horiz_advance)/2, 25)

		self.tb_device = evas.Textblock(self.canvas, pos=(120, 110), size=(350, 400), )
		self.tb_device.layer = 99
		self.tb_device.style_set(STYLE)

		self.image = evas.Image(self.canvas, )
		self.image.pass_events = True
		self.image.layer = 99

		for pos, text in enumerate(["back", "previous", "next", "power.on"]):
			self.buttons[text] = self.init_button(text, (pos+1)*16+pos*100, 524, 100, 100)

	def init_button(self, name, x, y, dx, dy):
		def button_callback(source, event):
			if name == 'back':
				PyneoController.show_dialer_screen()
			elif name == 'next':
				pass
			elif name == 'previous':
				pass
			elif name == 'power.on':
				PyneoController.powered_news('true')
			print '--- ', name
		button = evas.Image(self.canvas, pos=(x,y), size=(dx,dy), file="%s%s.png" % (THEME_IMAGES, name))
		button.fill = 0, 0, dx, dy
		button.layer = 99
		button.on_mouse_up_add(button_callback)
		return button

	def on_show_news(self, status):
		self.tb_device.text_markup_set(
			"%s, %s<br>%s" % (
			status['created'].encode('utf-8'),
			status['origin'].encode('utf-8'),
			status['title'].encode('utf-8')))
		if 'image' in status:
			print 'IMAGE PATH: ', status['image'][7:]
			self.image.file_set(status['image'][7:])
			self.set_image_size(10, 10, 100, 300)

	def set_image_size(self, x1, y1, dx, dy):
		x, y = self.image.image_size
		if x * dy > y * dx:
			y = y * dx / x
			x = dx
		else:
			x = x * dy / y
			y = dy
		print 'x, y, dx, dy: ', x, y, dx, dy
		self.image.geometry = x1+(dx-x)/2, y1+(dy-y)/2, x, y
		self.image.fill = 0, 0, x, y

	def show(self):
		self.bg.show()
		self.headline.show()
		self.tb_device.show()
		self.image.show()
		for text in ["back", "previous", "next", "power.on"]:
			self.buttons[text].show()

	def hide(self):
		self.bg.hide()
		self.headline.hide()
		self.tb_device.hide()
		self.image.hide()
		for text in ["back", "previous", "next", "power.on"]:
			self.buttons[text].hide()

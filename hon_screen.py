#!/usr/bin/env python2.5
# -*- coding: utf-8 -*-
__author__ = "M. Dietrich <mdt@pyneo.org>, F. Gau (fgau@pyneo.org), Thomas Gstaedtner (thomas (a) gstaedtner (.) net), Johannes 'josch' Schauer <j.schauer@email.de>"
__version__ = "prototype"
__copyright__ = "Copyright (c) 2009"
__license__ = "GPL3"

from epydial import *
from shutil import copy

class HonScreen():
	def register_pyneo_callbacks(self):
		pass

	def __init__(self, screen_manager):
		self.fullscreen = False
		self.rotation = False
		self.buttons = {}
		self.canvas = screen_manager.get_evas()

		self.image = evas.Image(self.canvas, )
		self.image.pass_events = True
		self.image.layer = 100
		PyneoController.get_hon(self.get_hon_cb)

		def background_callback(source, event):
			if self.fullscreen:
				if self.rotation:
					self.image.rotate(3)
					self.rotation = False
				self.set_image_size(20, 140, 440, 380)
				self.fullscreen = False
			else:
				x, y = self.image.image_size
				if x > y:
					self.image.rotate(1)
					self.rotation = True
				self.set_image_size(0, 0, 480, 640)
				self.fullscreen = True

		self.bg = evas.Image(self.canvas, pos=(0, 0), size=(WIDTH, HEIGHT), file=PyneoController.set_bg_image)
		self.bg.fill = 0, 0, WIDTH, HEIGHT
		self.bg.layer = 99
		self.bg.on_mouse_up_add(background_callback)

		self.headline = evas.Text(self.canvas, text="hot or not", font=("Sans:style=Bold,Edje-Vera", 60), color="#808080")
		self.headline.layer = 99
		self.headline.pos = ((480-self.headline.horiz_advance)/2, 25)

		self.subheadline = evas.Text(self.canvas, text="nick ???", font=("Sans:style=Bold,Edje-Vera", 22), color="#808080")
		self.subheadline.layer = 99
		self.subheadline.pos = ((WIDTH-self.subheadline.horiz_advance)/2, 110)

		for pos, text in enumerate(["back", "previous", "next"]):
			self.buttons[text] = self.init_button(text, (pos+1)*16+pos*100, 524, 100, 100)

	def init_button(self, name, x, y, dx, dy):
		def button_callback(source, event):
			if name == 'back':
				PyneoController.show_dialer_screen()
			elif name == 'next':
				PyneoController.vote_hon(self.nothot)
				PyneoController.get_hon(self.get_hon_cb)
			elif name == 'previous':
				PyneoController.vote_hon(self.hot)
				copy(self.image.file[0], "%s/%s.jpg"%(PIX_FILE_PATH, self.nick))
				PyneoController.get_hon(self.get_hon_cb)
			print '--- ', name
		button = evas.Image(self.canvas, pos=(x,y), size=(dx,dy), file="/usr/share/epydial/data/themes_data/blackwhite/images/%s.png" % name)
		button.fill = 0, 0, dx, dy
		button.layer = 99
		button.on_mouse_up_add(button_callback)
		return button

	def get_hon_cb(self, status):
		img = object_by_url(status['img']).read()
		pix = status['img']
		assert pix.startswith('file://')
		pix = pix[7:]
		self.nick = status['nick']
		self.subheadline.text = ('nick: %s' % self.nick)
		self.subheadline.pos = ((WIDTH-self.subheadline.horiz_advance)/2, 110)
		self.hot = dict(url=status['hot'])
		self.nothot = dict(url=status['nothot'])

		self.image.file_set(pix)
		self.set_image_size(20, 140, 440, 380)
		print 'img: ', self.image.file[0]

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

	def hide(self):
		self.bg.hide()
		self.headline.hide()
		self.subheadline.hide()
		self.image.hide()

		for pos, text in enumerate(["back", "previous", "next"]):
			self.buttons[text].hide()

	def show(self):
		self.bg.show()
		self.headline.show()
		self.subheadline.show()
		self.image.show()

		for pos, text in enumerate(["back", "previous", "next"]):
			self.buttons[text].show()

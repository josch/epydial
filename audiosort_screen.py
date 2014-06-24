#!/usr/bin/env python2.5
# -*- coding: utf-8 -*-
from __future__ import with_statement
__author__ = "F. Gau <fgau@pyneo.org>"
__version__ = "prototype"
__copyright__ = "Copyright (c) 2009"
__license__ = "GPL3"

from epydial import *

class AudiosortScreen():

	def register_pyneo_callbacks(self):
		PyneoController.register_callback("on_get_playlist", self.on_get_playlist)

	def __init__(self, screen_manager):
		self.FONT_COLOR = PyneoController.set_font_color
		self.buttons = {}
		self.keys = {}
		self.canvas = screen_manager.get_evas()

		self.bg = evas.Image(self.canvas, pos=(0, 0), size=(WIDTH, HEIGHT), file=PyneoController.set_bg_image)
		self.bg.fill = 0, 0, WIDTH, HEIGHT
		self.bg.layer = 99

		self.headline = evas.Text(self.canvas, text="music", font=("Sans:style=Bold,Edje-Vera", 60), color=self.FONT_COLOR)
		self.headline.layer = 99
		self.headline.pos = ((WIDTH-self.headline.horiz_advance)/2, 25)

		for pos, text in enumerate(["back", "previous", "next", "forward"]):
			self.buttons[text] = self.init_button(text, (pos+1)*16+pos*100, 524, 100, 100)

		for pos, text in enumerate(["artist", "album", "title"]):
			self.keys[text] = self.init_key(text, (pos+1)*100+60)

	def init_key(self, name, y):
		def key_callback(source, event):
			PyneoController.sort_playlist('asc', name)
			print '--- ', name
			PyneoController.get_playlist()
			PyneoController.show_audio_screen()
		key = evas.Text(self.canvas, text=name, font=("Sans:style=Bold,Edje-Vera", 50), color=self.FONT_COLOR)
		key.layer = 99
		key.pos = ((WIDTH-key.horiz_advance)/2, y)
		key.on_mouse_up_add(key_callback)
		return key

	def init_button(self, name, x, y, dx, dy):
		def button_callback(source, event):
			if name == 'back':
				PyneoController.show_dialer_screen()
			elif name == 'next':
				pass
			elif name == 'previous':
				pass
			elif name == 'forward':
				PyneoController.show_audio_screen()
			print '--- ', name
		button = evas.Image(self.canvas, pos=(x,y), size=(dx,dy), file="%s%s.png" % (THEME_IMAGES, name))
		button.fill = 0, 0, dx, dy
		button.layer = 99
		button.on_mouse_up_add(button_callback)
		return button

	def on_get_playlist(self, status):
		print 'Playlist', status

	def show(self):
		self.bg.show()
		self.headline.show()
		for text in ["back", "previous", "next", "forward"]:
			self.buttons[text].show()
		for text in ["artist", "album", "title"]:
			self.keys[text].show()

	def hide(self):
		self.bg.hide()
		self.headline.hide()
		for text in ["back", "previous", "next", "forward"]:
			self.buttons[text].hide()
		for text in ["artist", "album", "title"]:
			self.keys[text].hide()

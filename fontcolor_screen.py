#!/usr/bin/env python2.5
# -*- coding: utf-8 -*-
__author__ = "M. Dietrich <mdt@pyneo.org>, F. Gau (fgau@pyneo.org), Thomas Gstaedtner (thomas (a) gstaedtner (.) net), Johannes 'josch' Schauer <j.schauer@email.de>"
__version__ = "prototype"
__copyright__ = "Copyright (c) 2009"
__license__ = "GPL3"

from epydial import *

class FontcolorScreen():
	def register_pyneo_callbacks(self):
		pass

	def __init__(self, screen_manager):
		FONT_COLOR = PyneoController.set_font_color
		self.red = int(FONT_COLOR[3:5], 16)
		self.green = int(FONT_COLOR[5:7], 16)
		self.blue = int(FONT_COLOR[7:], 16)
		self.alpha = int(FONT_COLOR[1:3], 16)
		self.buttons = {}
		self.settings = {}
		self.canvas = screen_manager.get_evas()

		self.bg = evas.Image(self.canvas, pos=(0, 0), size=(WIDTH, HEIGHT), file=PyneoController.set_bg_image)
		self.bg.fill = 0, 0, WIDTH, HEIGHT
		self.bg.layer = 97

		self.headline = evas.Text(self.canvas, text="colors", font=("Sans:style=Bold,Edje-Vera", 60), color=FONT_COLOR)
		self.headline.layer = 99
		self.headline.pos = ((480-self.headline.horiz_advance)/2, 25)

		for pos, text in enumerate(["back", "forward", "yes"]):
			self.buttons[text] = self.init_button(text, (pos+1)*16+pos*100, 524, 100, 100)

		for pos, text in enumerate(["red", "green", "blue", "alpha"]):
			for i, row in enumerate(["left", "right", "description", "box", "plus", "minus"]):
				self.settings[text, row] = self.init_settings(row, text, (pos+1)*25+pos*75+100)

		self.set_bar_description('red', self.red)
		self.set_bar_description('green', self.green)
		self.set_bar_description('blue', self.blue)
		self.set_bar_description('alpha', self.alpha)

	def set_bar_description(self, color, status):
		self.settings[color, 'description'].text = '%s: %s' % (color, status)
		x, y = self.settings[color, 'description'].pos_get()
		self.settings[color, 'description'].pos = ((WIDTH-self.settings[color, 'description'].horiz_advance)/2, y)

	def init_settings(self, row, name, y):
		FONT_COLOR = PyneoController.set_font_color
		def button_callback(source, event):
			if name == 'red' and row == 'right':
				if self.red != 255:
					self.red += 1
			elif name == 'red' and row == 'left':
				if self.red != 0:
					self.red -= 1
			elif name == 'green' and row == 'right':
				if self.green != 255:
					self.green += 1
			elif name == 'green' and row == 'left':
				if self.green != 0:
					self.green -= 1
			elif name == 'blue' and row == 'right':
				if self.blue != 255:
					self.blue += 1
			elif name == 'blue' and row == 'left':
				if self.blue != 0:
					self.blue -= 1
			elif name == 'alpha' and row == 'right':
				if self.alpha != 255:
					self.alpha += 1
			elif name == 'alpha' and row == 'left':
				if self.alpha != 0:
					self.alpha -= 1
			self.set_bar_description('red', self.red)
			self.set_bar_description('green', self.green)
			self.set_bar_description('blue', self.blue)
			self.set_bar_description('alpha', self.alpha)
			self.headline.color_set(self.red, self.green, self.blue, self.alpha)
			print '--- ', name, row
		if row == 'left':
			bg_left = evas.Rectangle(self.canvas, pos=(0,y), size=(WIDTH/2,80), color="#00ffffff")
			bg_left.layer = 99
			bg_left.on_mouse_up_add(button_callback)
			return bg_left
		if row == 'right':
			bg_right = evas.Rectangle(self.canvas, pos=(WIDTH/2,y), size=(WIDTH/2,80), color="#00ffffff")
			bg_right.layer = 99
			bg_right.on_mouse_up_add(button_callback)
			return bg_right
		if row == 'description':
			description = evas.Text(self.canvas, font=("Sans:style=Edje-Vera", 18), color=FONT_COLOR)
			description.text = '%s:' % name
			description.pos = ((WIDTH-description.horiz_advance)/2, y+26)
			description.layer = 99
			return description
		if row == 'box':
			box = evas.Rectangle(self.canvas, pos=(WIDTH/4,y+20), size=(WIDTH/2,40), color='#%02x%02x%02x%02x' % (self.alpha/2, self.red, self.green, self.blue))
			box.layer = 98
			return box
		if row == 'plus':
			plus = evas.Text(self.canvas, text="+", pos=(420,y), font=("Sans:style=Edje-Vera", 46), color=FONT_COLOR)
			plus.layer = 98
			return plus
		if row == 'minus':
			minus = evas.Text(self.canvas, text="-", pos=(40, y), font=("Sans:style='Edje-Vera", 46), color=FONT_COLOR)
			minus.layer = 98
			return minus

	def init_button(self, name, x, y, dx, dy):
		def button_callback(source, event):
			if name == 'back':
				PyneoController.show_screen(SETTINGS_SCREEN_NAME)
			elif name == 'forward':
			        PyneoController.show_screen(SIMIMPORTER_SCREEN_NAME)
			elif name == "yes":
				PyneoController.set_ini_value('theme', 'font_color', '#%02x%02x%02x%02x' % (self.alpha, self.red, self.green, self.blue))
				PyneoController.reload_font_color()
#				PyneoController.show_screen(FONTCOLOR_SCREEN_NAME)
			print '--- ', name
		button = evas.Image(self.canvas, pos=(x,y), size=(dx,dy), file="%s%s.png" % (THEME_IMAGES, name))
		button.fill = 0, 0, dx, dy
		button.layer = 99
		button.on_mouse_up_add(button_callback)
		return button

	def show(self):
		self.bg.show()
		self.headline.show()
		for text in ["red", "green", "blue", "alpha"]:
			for row in ["left", "right", "description", "box", "plus", "minus"]:
				self.settings[text, row].show()
		for text in ["back", "forward", "yes"]:
			self.buttons[text].show()

	def hide(self):
		self.bg.hide()
		self.headline.hide()
		for text in ["red", "green", "blue", "alpha"]:
			for row in ["left", "right", "description", "box", "plus", "minus"]:
				self.settings[text, row].hide()
		for text in ["back", "forward", "yes"]:
			self.buttons[text].hide()

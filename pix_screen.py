#!/usr/bin/env python2.5
# -*- coding: utf-8 -*-
__author__ = "F. Gau (fgau@pyneo.org), Thomas Gstaedtner (thomas (a) gstaedtner (.) net), Johannes 'josch' Schauer <j.schauer@email.de>"
__version__ = "prototype"
__copyright__ = "Copyright (c) 2009"
__license__ = "GPL3"

from epydial import *

class PixScreen():
	def register_pyneo_callbacks(self):
		pass

	pix_pointer = 0

	def __init__(self, screen_manager):
		self.FONT_COLOR = PyneoController.set_font_color
		self.fullscreen = False
		self.rotation = False
		self.buttons = {}
		self.canvas = screen_manager.get_evas()

		self.image = evas.Image(self.canvas, )
		self.image.pass_events = True
		self.image.layer = 100

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
				self.set_image_size(0, 0, WIDTH, HEIGHT)
				self.fullscreen = True

		self.bg = evas.Image(self.canvas, pos=(0, 0), size=(WIDTH, HEIGHT), file=PyneoController.set_bg_image)
		self.bg.fill = 0, 0, WIDTH, HEIGHT
		self.bg.layer = 99
		self.bg.on_mouse_up_add(background_callback)

		def headline_callback(source, event):
			if source:
				self.bg_popup.show()
				self.save_popup.show()
				self.buttons["yes"].show()
				self.buttons["no"].show()

		self.headline = evas.Text(self.canvas, text="pix viewer", font=("Sans:style=Bold,Edje-Vera", 60), color=self.FONT_COLOR)
		self.headline.layer = 99
		self.headline.pos = ((WIDTH-self.headline.horiz_advance)/2, 25)
		self.headline.on_mouse_up_add(headline_callback)

		self.subheadline = evas.Text(self.canvas, font=("Sans:style=Bold,Edje-Vera", 22), color=self.FONT_COLOR)

		self.bg_popup = evas.Rectangle(self.canvas, pos=(0,0), size=(WIDTH,HEIGHT), color="#bb000000")
		self.bg_popup.layer = 100

		self.save_popup = evas.Text(self.canvas, text="save as background?", font=("Sans:style=Bold,Edje-Vera", 25), color=self.FONT_COLOR)
		self.save_popup.layer = 100
		self.save_popup.pos = ((WIDTH-self.save_popup.horiz_advance)/2, (HEIGHT-self.save_popup.vert_advance)/2)

		self.subheadline.layer = 99
		self.subheadline.pos = ((WIDTH-self.subheadline.horiz_advance)/2, 110)

		for pos, text in enumerate(["back", "previous", "next", "rotate"]):
			self.buttons[text] = self.init_button(text, (pos+1)*16+pos*100, 524, 100, 100, 99)

		self.buttons["yes"] = self.init_button("yes", 16, 408, 100, 100, 100)
		self.buttons["no"] = self.init_button("no", 364, 408, 100, 100, 100)

		self.objects = listdir(PIX_FILE_PATH)
		if self.objects:
			self.on_get_pix()

	def init_button(self, name, x, y, dx, dy, layer):
		def button_callback(source, event):
			if name == 'back':
				PyneoController.show_dialer_screen()
			elif name == 'next':
				if self.objects:
					self.pix_pointer = (self.pix_pointer+1)%len(self.objects)
					self.on_get_pix()
			elif name == 'previous':
				if self.objects:
					self.pix_pointer = (self.pix_pointer-1)%len(self.objects)
					self.on_get_pix()
			elif name == 'rotate':
				self.image.rotate(1)
				self.set_image_size(20, 140, 440, 380)
			elif name == 'no':
				self.hide_popup()
			elif name == 'yes':
				self.hide_popup()
				PyneoController.set_ini_value('theme', 'bg_image', PIX_FILE_PATH + self.subheadline.text)
			print '--- ', name
		button = evas.Image(self.canvas, pos=(x,y), size=(dx,dy), file="%s%s.png" % (THEME_IMAGES, name))
		button.fill = 0, 0, dx, dy
		button.layer = layer
		button.on_mouse_up_add(button_callback)
		return button

	def on_get_pix(self):
		self.subheadline.text = self.objects[self.pix_pointer]
		self.subheadline.pos = ((WIDTH-self.subheadline.horiz_advance)/2, 110)
		self.image.file_set(PIX_FILE_PATH + self.objects[self.pix_pointer])
		self.set_image_size(20, 140, 440, 380)

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

	def hide_popup(self):
		self.buttons["yes"].hide()
		self.buttons["no"].hide()
		self.bg_popup.hide()
		self.save_popup.hide()

	def hide(self):
		self.bg.hide()
		self.headline.hide()
		self.subheadline.hide()
		self.image.hide()
		for text in ["back", "previous", "next", "rotate"]:
			self.buttons[text].hide()

	def show(self):
		self.bg.show()
		self.headline.show()
		self.subheadline.show()
		self.objects = listdir(PIX_FILE_PATH)
		self.image.show()
		for text in ["back", "previous", "next", "rotate"]:
			self.buttons[text].show()

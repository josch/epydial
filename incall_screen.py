#!/usr/bin/env python2.5
# -*- coding: utf-8 -*-
__author__ = "Soeren Apel (abraxa@dar-clan.de), Frank Gau (fgau@gau-net.de), Thomas Gstaedtner (thomas (a) gstaedtner (.) net)"
__version__ = "prototype"
__copyright__ = "Copyright (c) 2008"
__license__ = "GPL3"

from epydial import *

class InCallScreen():
	def register_pyneo_callbacks(self):
		PyneoController.register_callback("gsm_number_display", self.on_gsm_number_display)

	def on_gsm_number_display(self, number):
		self.number = number
		print 'SELF.NUMBER: ', self.number
		self.speaker = True
		name = DatabaseController.get_name_from_number(self.number)
		if name:
			self.number_text.text = name
		else:
			self.number_text.text =  self.number
		self.headline.text = 'call %s' % PyneoController.call_type
		self.headline.pos = ((WIDTH-self.headline.horiz_advance)/2, 25)
		self.number_text.pos = ((WIDTH-self.number_text.horiz_advance)/2, (HEIGHT-self.number_text.vert_advance)/2)

	def __init__(self, screen_manager):
		self.canvas = screen_manager.get_evas()
		self.buttons = {}

		self.bg = evas.Image(self.canvas, pos=(0, 0), size=(WIDTH, HEIGHT), file=PyneoController.set_bg_image)
		self.bg.fill = 0, 0, WIDTH, HEIGHT
		self.bg.layer = 99

		self.headline = evas.Text(self.canvas, text="call", font=("Sans:style=Bold,Edje-Vera", 60), color="#808080")
		self.headline.layer = 99

		self.number_text = evas.Text(self.canvas, font=("Sans:style=Bold,Edje-Vera", 30), color="#808080")
		self.number_text.layer = 99

		for pos, text in enumerate(["yes", "no", "speaker_off"]):
			self.buttons[text] = self.init_button(text, (pos+1)*16+pos*100, 524, 100, 100)

	def button_callback(self, source, event):
		if source.name == 'yes':
			PyneoController.stop_tone('ring')
			PyneoController.gsm_accept(self.number)
		elif source.name == 'no':
			PyneoController.stop_tone('ring')
			PyneoController.gsm_hangup()
			PyneoController.show_dialer_screen()
		elif source.name == 'speaker_off' and self.speaker:
			PyneoController.set_state_file('gsmspeakerout')
			self.buttons['speaker_off'].file = '%sspeaker_on.png' % THEME_IMAGES
			self.speaker = False
		elif source.name == 'speaker_off' and not self.speaker:
			PyneoController.set_state_file('gsmhandset')
			self.buttons['speaker_off'].file = '%sspeaker_off.png' % THEME_IMAGES
			self.speaker = True
		print '--- ', source.name

	def init_button(self, name, x, y, dx, dy):
		button = evas.Image(self.canvas, pos=(x,y), size=(dx,dy), file="%s%s.png" % (THEME_IMAGES, name))
		button.fill = 0, 0, dx, dy
		button.layer = 99
		button.on_mouse_up_add(self.button_callback)
		button.name = name
		return button

	def show(self):
		self.bg.show()
		self.headline.show()
		self.number_text.show()

		for pos, text in enumerate(["yes", "no", "speaker_off"]):
			self.buttons[text].show()

	def hide(self):
		self.bg.hide()
		self.headline.hide()
		self.number_text.hide()

		for pos, text in enumerate(["yes", "no", "speaker_off"]):
			self.buttons[text].hide()

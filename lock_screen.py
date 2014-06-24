#!/usr/bin/env python2.5
# -*- coding: utf-8 -*-
__author__ = "Johannes 'josch' Schauer <josch@pyneo.org>, F. Gau <fgau@pyneo.org>"
__version__ = "prototype"
__copyright__ = "Copyright (c) 2009 J. Schauer"
__license__ = "GPL3"

# Todo: synchron with other clock => numberdisplay_text

from epydial import *

class LockScreen():
	def register_pyneo_callbacks(self):
		pass

	def __init__(self, screen_manager):
		self.canvas = screen_manager.get_evas()

		self.bg = evas.Rectangle(self.canvas, pos=(0,0), size=(WIDTH, HEIGHT), color="#bb000000")
		self.bg.on_mouse_up_add(self.on_mouse_up)
		self.bg.layer = 99

		self.button = evas.Rectangle(self.canvas, pos=(0,0), size=(WIDTH/3,HEIGHT/3), color="#00000000")
		self.button.on_mouse_up_add(self.on_mouse_up)
		self.button.layer = 100

		self.label = evas.Text(self.canvas, text="screen locked", font=("sans serif", 50), color="#808080")
		self.label.layer = 100
		self.label.pass_events = True
		self.label.pos = ((WIDTH-self.label.horiz_advance)/2, (HEIGHT-self.label.vert_advance)/2)

		self.time_label = evas.Text(self.canvas, text="clock", font=("sans serif", 30), color="#808080")
		self.time_label.layer = 100
		self.time_label.pass_events = True

		self.state = 0

		ecore.timer_add(10.0, self.display_time)
		self.display_time()

	def on_mouse_up(self, source, event):
		if source == self.bg:
			self.state = 0
			self.button.pos = (0, 0)
		else:
			if self.state == 0:
				self.button.pos = ((WIDTH*2)/3, 0)
			elif self.state == 1:
				self.button.pos = ((WIDTH*2)/3, (HEIGHT*2)/3)
			elif self.state == 2:
				self.button.pos = (0, (HEIGHT*2)/3)
			else:
				self.button.pos = (0, 0)
				PyneoController.show_dialer_screen()
			self.state = (self.state+1)%4

	def show(self):
		self.bg.show()
		self.button.show()
		self.label.show()
		self.time_label.show()

	def hide(self):
		self.bg.hide()
		self.button.hide()
		self.label.hide()
		self.time_label.hide()

	def display_time(self):
		now = datetime.now()
		datetimestring = now.strftime('%a, %d %b %Y %H:%M')
		self.time_label.pos = ((WIDTH-self.time_label.horiz_advance)/2, (HEIGHT-self.time_label.vert_advance)/2+50)
		self.time_label.text_set(datetimestring)
		return True

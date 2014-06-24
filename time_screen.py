#!/usr/bin/env python2.5
# -*- coding: utf-8 -*-
__author__ = "F. Gau (fgau@gau-net.de), Johannes 'josch' Schauer <j.schauer@email.de>"
__version__ = "prototype"
__copyright__ = "Copyright (c) 2009"
__license__ = "GPL3"

from epydial import *

class TimeScreen(EdjeGroup):
	def __init__(self, screen_manager):
		EdjeGroup.__init__(self, screen_manager, TIME_SCREEN_NAME)
		self.alarm = "00:00"
		self.stopwatch_state = 0

	def register_pyneo_callbacks(self):
		pass
		#PyneoController.register_callback("brightness_change", self.on_brightness_change)

	@edje.decorators.signal_callback("mouse,up,1", "*")
	def on_edje_signal_settings_screen_triggered(self, emission, source):
		if source == "back":
			PyneoController.show_dialer_screen()
		elif source == "alarm":
			PyneoController.dialer_text_set("alarm %s"%self.alarm)
			PyneoController.show_dialer_screen()
		elif source == "countdown":
			PyneoController.dialer_text_set("count %s"%self.alarm)
			PyneoController.show_dialer_screen()
		elif source == "stopwatch":
			if self.stopwatch_state == 0:
				self.stopwatch_state = 1
			elif self.stopwatch_state == 1:
				self.stopwatch_state = 2
			elif self.stopwatch_state == 2:
				self.stopwatch_state = 0
		print source

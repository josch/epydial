#!/usr/bin/env python2.5
# -*- coding: utf-8 -*-
__author__ = "Soeren Apel (abraxa@dar-clan.de), F. Gau (fgau@pyneo.org), Thomas Gstaedner (thomas (a) gstaedtner (.) net)"
__version__ = "prototype"
__copyright__ = "Copyright (c) 2008"
__license__ = "GPL3"

from epydial import *

STYLE = """
DEFAULT='font=Sans font_size=20 align=left color=#808080 wrap=word valign=top'
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

class WlanScreen():
	def register_pyneo_callbacks(self):
		PyneoController.register_callback("scan_wireless", self.on_scan_wireless)

	def on_scan_wireless(self, status):
		wireless = 'networks:<br><br>'
		for n, v in status.items():
			wireless += '%s, %s, %s, %s, %s<br>' % (n, v['essid'], v['encryption_key'], v['quality'], v['channel'])
			print 'network', n, v['essid'], v['quality'], v['encryption_key'], v['address']
		self.tb.text_markup_set(wireless)

	def __init__(self, screen_manager):
		self.buttons = {}
		self.contents = {}
		self.canvas = screen_manager.get_evas()

		self.bg = evas.Image(self.canvas, pos=(0, 0), size=(WIDTH, HEIGHT), file=PyneoController.set_bg_image)
		self.bg.fill = 0, 0, WIDTH, HEIGHT
		self.bg.layer = 99

		self.headline = evas.Text(self.canvas, text="wlan", font=("Sans:style=Bold,Edje-Vera", 60), color="#808080")
		self.headline.layer = 99
		self.headline.pos = ((480-self.headline.horiz_advance)/2, 25)

		self.tb = evas.Textblock(self.canvas, pos=(10, 100), size=(460, 600), )
		self.tb.layer = 99
		self.tb.style_set(STYLE)

		for pos, text in enumerate(["back", "previous", "next"]):
			self.buttons[text] = self.init_button(text, (pos+1)*16+pos*100, 524, 100, 100)

	def init_button(self, name, x, y, dx, dy):
		def button_callback(source, event):
			if name == 'back':
				PyneoController.show_dialer_screen()
			elif name == 'next':
				PyneoController.scan_wireless()
			elif name == 'previous':
				pass
			print '--- ', name
		button = evas.Image(self.canvas, pos=(x,y), size=(dx,dy), file="%s%s.png" % (THEME_IMAGES, name))
		button.fill = 0, 0, dx, dy
		button.layer = 99
		button.on_mouse_up_add(button_callback)
		return button

	def show(self):
		self.bg.show()
		self.headline.show()
		self.tb.show()
		for text in ["back", "previous", "next"]:
			self.buttons[text].show()

	def hide(self):
		self.bg.hide()
		self.headline.hide()
		self.tb.hide()
		for text in ["back", "previous", "next"]:
			self.buttons[text].hide()

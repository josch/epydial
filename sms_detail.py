#!/usr/bin/env python2.5
# -*- coding: utf-8 -*-
__author__ = "Soeren Apel (abraxa@dar-clan.de), Frank Gau (fgau@pyneo.org), Thomas Gstaedtner (thomas (a) gstaedtner (.) net)"
__version__ = "prototype"
__copyright__ = "Copyright (c) 2008"
__license__ = "GPL3"

from epydial import *

STYLE = """
DEFAULT='font=Sans font_size=22 align=left color=#808080 wrap=word valign=top'
p='+ '
/p='- \\n \\n'
br='\\n'
center='+ align=center'
/center='-'
"""

class SmsDetail():

	def __init__(self, screen_manager):

		self.buttons = {}
		self.header = {}
		self.canvas = screen_manager.get_evas()

		self.bg = evas.Image(self.canvas, pos=(0, 0), size=(WIDTH, HEIGHT), file=PyneoController.set_bg_image)
		self.bg.fill = 0, 0, WIDTH, HEIGHT
		self.bg.layer = 99

		self.headline = evas.Text(self.canvas, text="sms detail", font=("Sans:style=Bold,Edje-Vera", 60), color="#808080")
		self.headline.layer = 99
		self.headline.pos = ((WIDTH-self.headline.horiz_advance)/2, 25)

		self.bg_popup = evas.Rectangle(self.canvas, pos=(0,0), size=(WIDTH,HEIGHT), color="#bb000000")
		self.bg_popup.layer = 100

		self.save_popup = evas.Text(self.canvas, text="delete sms?", font=("Sans:style=Bold,Edje-Vera", 25), color="#808080")
		self.save_popup.layer = 100
		self.save_popup.pos = ((WIDTH-self.save_popup.horiz_advance)/2, (HEIGHT-self.save_popup.vert_advance)/2)

		self.tb = evas.Textblock(self.canvas, pos=(10, 240), size=(460, 260), )
		self.tb.layer = 99
		self.tb.style_set(STYLE)

		for pos, text in enumerate(["back", "previous", "next", "no"]):
			self.buttons[text] = self.init_button(text, (pos+1)*16+pos*100, 524, 100, 100, 99)

		self.buttons["yes"] = self.init_button("yes", 16, 408, 100, 100, 100)
		self.buttons["nono"] = self.init_button("nono", 364, 408, 100, 100, 100)

		for pos, row in enumerate(["sms_from", "sms_time", "sms_status"]):
			self.header[row] = self.init_header(row, 10, pos+150)

	def init_header(self, row, x, y):
		if row == 'sms_from':
			sms_from = evas.Text(self.canvas, font=("Sans:style=Edje-Vera", 18), color="#808080")
			sms_from.pos = (10, y+10)
			sms_from.text = 'from:'
			sms_from.layer = 99
			return sms_from
		if row == 'sms_time':
			sms_time = evas.Text(self.canvas, font=("Sans:style=Edje-Vera", 18), color="#808080")
			sms_time.pos = (10, y+30)
			sms_time.text = 'time:'
			sms_time.layer = 99
			return sms_time
		if row == 'sms_status':
			sms_status = evas.Text(self.canvas, font=("Sans:style=Edje-Vera", 18), color="#808080")
			sms_status.pos = (10, y+50)
			sms_status.text = 'status:'
			sms_status.layer = 99
			return sms_status

	def init_button(self, name, x, y, dx, dy, layer):
		def button_callback(source, event):
			if name == 'back':
				PyneoController.show_dialer_screen()
			elif name == 'next':
				pass
			elif name == 'previous':
				pass
			elif name == 'no':
				self.bg_popup.show()
				self.save_popup.show()
				self.buttons["yes"].show()
				self.buttons["nono"].show()
			elif name == 'nono':
				self.hide_popup()
			elif name == 'yes':
				DatabaseController.delete_sms(self.header['sms_time'].text[6:])
				self.hide_popup()
				PyneoController.dialer_screen()
			print '--- ', name
		if name == 'nono':
			button = evas.Image(self.canvas, pos=(x,y), size=(dx,dy), file="%sno.png" % THEME_IMAGES)
		else:
			button = evas.Image(self.canvas, pos=(x,y), size=(dx,dy), file="%s%s.png" % (THEME_IMAGES, name))
		button.fill = 0, 0, dx, dy
		button.layer = layer
		button.on_mouse_up_add(button_callback)
		return button

	def register_pyneo_callbacks(self):
		PyneoController.register_callback("show_sms_detail", self.on_show_sms_detail)

	def on_show_sms_detail(self, sms_number, sms_status):
		results = DatabaseController.get_sms_detail(sms_number, sms_status)
		self.header['sms_from'].text = 'from: %s' %results[0][1]
		self.header['sms_time'].text = 'time: %s' %results[0][3]
		self.header['sms_status'].text = 'status: %s' %results[0][0]
		self.tb.text_markup_set(results[0][2].encode('utf8'))
		name = DatabaseController.get_name_from_number(results[0][1])
		if name:
			self.header['sms_from'].text = 'from: %s' %name
		if results[0][0] == 'REC UNREAD':
			DatabaseController.mark_sms_read(results[0][3])

	def hide_popup(self):
		self.bg_popup.hide()
		self.save_popup.hide()
		self.buttons["yes"].hide()
		self.buttons["nono"].hide()

	def show(self):
		self.bg.show()
		self.headline.show()
		self.tb.show()
		for text in ["back", "previous", "next", "no"]:
			self.buttons[text].show()

		for pos, row in enumerate(["sms_from", "sms_time", "sms_status"]):
			self.header[row].show()

	def hide(self):
		self.bg.hide()
		self.headline.hide()
		self.tb.hide()
		for text in ["back", "previous", "next", "no"]:
			self.buttons[text].hide()

		for row in ["sms_from", "sms_time", "sms_status"]:
			self.header[row].hide()

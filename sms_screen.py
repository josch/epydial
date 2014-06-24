#!/usr/bin/env python2.5
# -*- coding: utf-8 -*-
__author__ = "F. Gau (fgau@pyneo.org), Thomas Gstaedtner (thomas (a) gstaedtner (.) net)"
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

class SmsScreen():
	def register_pyneo_callbacks(self):
		pass

	sms_offset = 0
	sorted_by = 'REC UNREAD'
	detail = False

	def __init__(self, screen_manager):
		self.buttons = {}
		self.bg_line = {}
		self.canvas = screen_manager.get_evas()

		self.bg = evas.Image(self.canvas, pos=(0, 0), size=(WIDTH, HEIGHT), file=PyneoController.set_bg_image)
		self.bg.fill = 0, 0, WIDTH, HEIGHT
		self.bg.layer = 99

		def headline_callback(source, event):
			if self.sorted_by == "REC UNREAD":
				self.sorted_by = 'REC READ'
			else:
				self.sorted_by = 'REC UNREAD'
			self.sms_offset = 0
			self.subheadline.text = ('sorted by: %s' % self.sorted_by)
			self.subheadline.pos = ((WIDTH-self.subheadline.horiz_advance)/2, 100)
			self.show_sms()

		self.headline = evas.Text(self.canvas, text="sms", font=("Sans:style=Bold,Edje-Vera", 60), color="#808080")
		self.headline.layer = 99
		self.headline.pos = ((WIDTH-self.headline.horiz_advance)/2, 25)
		self.headline.on_mouse_up_add(headline_callback)

		self.subheadline = evas.Text(self.canvas, font=("Sans,Edje-Vera", 25), color="#808080")
		self.subheadline.layer = 99
		self.subheadline.pos = ((WIDTH-self.subheadline.horiz_advance)/2, 100)

		for pos, text in enumerate(["back", "previous", "next"]):
			self.buttons[text] = self.init_button(text, (pos+1)*16+pos*100, 524, 100, 100)

		for i, text in enumerate(["1" ,"2", "3", "4", "5"]):
			for j, row in enumerate(["date", "content", "bg"]):
				self.bg_line[text, row] = self.init_line(row, text, i)

		if DatabaseController.check_for_unread_sms() == 0:
			self.sorted_by = 'REC READ'
		else:
			self.sorted_by = 'REC UNREAD'

		self.show_sms()

	def init_line(self, row, name, num):
		def button_callback(source, event):
			if name == "1":
				PyneoController.show_screen(SMS_DETAIL_SCREEN_NAME)
				PyneoController.show_sms_detail(self.sms_offset, self.sorted_by)
			if name == "2":
				self.sms_offset += 1
				PyneoController.show_screen(SMS_DETAIL_SCREEN_NAME)
				PyneoController.show_sms_detail(self.sms_offset, self.sorted_by)
			if name == "3":
				self.sms_offset += 2
				PyneoController.show_screen(SMS_DETAIL_SCREEN_NAME)
				PyneoController.show_sms_detail(self.sms_offset, self.sorted_by)
			if name == "4":
				self.sms_offset += 3
				PyneoController.show_screen(SMS_DETAIL_SCREEN_NAME)
				PyneoController.show_sms_detail(self.sms_offset, self.sorted_by)
			if name == "5":
				self.sms_offset += 4
				PyneoController.show_screen(SMS_DETAIL_SCREEN_NAME)
				PyneoController.show_sms_detail(self.sms_offset, self.sorted_by)
			print '---', name

		if row == "bg":
			bg = evas.Rectangle(self.canvas, pos=(480/20, (640*2)/9+num*640/9+5), size=((480*18)/20, 640/12), color="#38ffffff")
			bg.layer = 99
			bg.on_mouse_up_add(button_callback)
			return bg

		if row == "date":
			date = evas.Text(self.canvas, font=("Sans:style=Edje-Vera", 18), color="#808080")
			date.pos = (480/20+10, (640*2)/9+num*640/9+5)
			date.layer = 99
			return date

		if row == "content":
			content = evas.Text(self.canvas, font=("Sans:style=Edje-Vera", 18), color="#808080")
			content.pos = (480/20+10, (640*2)/9+num*640/9+30)
			content.layer = 99
			return content


	def init_button(self, name, x, y, dx, dy):
		def button_callback(source, event):
			if name == 'back':
				PyneoController.show_dialer_screen()
			elif name == 'next':
				new_offset = self.sms_offset + 5
				if DatabaseController.get_sms_count(self.sorted_by) > new_offset:
					self.sms_offset = new_offset
					self.show_sms()
			elif name == 'previous':
				new_offset = self.sms_offset -5
				if new_offset >= 0:
					self.sms_offset = new_offset
					self.show_sms()
			print '--- ', name
		button = evas.Image(self.canvas, pos=(x,y), size=(dx,dy), file="%s%s.png" % (THEME_IMAGES, name))
		button.fill = 0, 0, dx, dy
		button.layer = 99
		button.on_mouse_up_add(button_callback)
		return button

	def del_displayed_sms(self):
		x=1
		while x < 6:
			self.bg_line[str(x), 'date'].text = ""
			self.bg_line[str(x), 'content'].text = ""
			x += 1

	def show_sms(self):
		x = 1
		self.detail = False
		self.del_displayed_sms()
		self.subheadline.text = ('sorted by: %s' % self.sorted_by)
		self.subheadline.pos = ((WIDTH-self.subheadline.horiz_advance)/2, 100)
		cursor = DatabaseController.get_sms_list(5, self.sms_offset, self.sorted_by)
		for i in cursor:
			number = i[1]
			name = DatabaseController.get_name_from_number(i[1])
			if name:
				self.bg_line[str(x), 'date'].text = ("%s, %s" %(i[3][:14], name))
			else:
				self.bg_line[str(x), 'date'].text = ("%s, %s" %(i[3][:14], number))
			self.bg_line[str(x), 'content'].text = i[2][:37].encode('utf8') + ' ...'
			x += 1

	def show(self):
		self.bg.show()
		self.headline.show()
		self.subheadline.show()

		for pos, text in enumerate(["back", "previous", "next"]):
			self.buttons[text].show()

		for i, text in enumerate(["1" ,"2", "3", "4", "5"]):
			for j, row in enumerate(["date", "content", "bg"]):
				self.bg_line[text, row].show()

	def hide(self):
		self.bg.hide()
		self.headline.hide()
		self.subheadline.hide()

		for pos, text in enumerate(["back", "previous", "next"]):
			self.buttons[text].hide()

		for i, text in enumerate(["1" ,"2", "3", "4", "5"]):
			for j, row in enumerate(["date", "content", "bg"]):
				self.bg_line[text, row].hide()

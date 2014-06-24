#!/usr/bin/env python2.5
# -*- coding: utf-8 -*-
__author__ = "F. Gau <fgau@pyneo.org>, Thomas 'thomasg' Gstaedtner <thomas (a) gstaedtner (.) net>"
__version__ = "prototype"
__copyright__ = "Copyright (c) 2009"
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

class HistoryScreen():
	calls_offset = 0
	sorted_by = ['time', 'missed', 'incoming', 'outgoing']
	sorted_by_state = 'time'

	def register_pyneo_callbacks(self):
		pass

	def __init__(self, screen_manager):
		self.buttons = {}
		self.bg_line = {}
		self.canvas = screen_manager.get_evas()

		PyneoController.set_missed_call_icon('false')
		PyneoController.set_ini_value('status', 'missed_calls', 'false')

		self.bg = evas.Image(self.canvas, pos=(0, 0), size=(WIDTH, HEIGHT), file=PyneoController.set_bg_image)
		self.bg.fill = 0, 0, WIDTH, HEIGHT
		self.bg.layer = 99

		def headline_callback(source, event):
			self.sorted_by_state = self.sorted_by[(self.sorted_by.index(self.sorted_by_state)+1)%len(self.sorted_by)]
			self.calls_offset = 0
			self.subheadline.text = ('sorted by: %s' % self.sorted_by_state)
			self.subheadline.pos = ((WIDTH-self.subheadline.horiz_advance)/2, 100)
			self.show_calls()

		self.headline = evas.Text(self.canvas, text="call history", font=("Sans:style=Bold,Edje-Vera", 60), color="#808080")
		self.headline.layer = 99
		self.headline.pos = ((WIDTH-self.headline.horiz_advance)/2, 25)
		self.headline.on_mouse_up_add(headline_callback)

		self.subheadline = evas.Text(self.canvas, font=("Sans,Edje-Vera", 25), color="#808080")
		self.subheadline.layer = 99

		for pos, text in enumerate(["back", "previous", "next"]):
			self.buttons[text] = self.init_button(text, (pos+1)*16+pos*100, 524, 100, 100)

		for i, text in enumerate(["1" ,"2", "3", "4", "5"]):
			for j, row in enumerate(["status", "date", "number", "bg"]):
				self.bg_line[text, row] = self.init_line(row, text, i)

		self.show_calls()

	def init_line(self, row, name, num):
		def button_callback(source, event):
			if name == '1' or name == '2' or name == '3' or name == '4' or name == '5':
				PyneoController.dialer_text_set(self.bg_line[name, 'number'].text)
				PyneoController.show_dialer_screen()
			print '---', name

		if row == "status":
			status = evas.Image(self.canvas, size=(33,33))
			status.pos = (480/20+10, (640+2)/9+num*640/9+85)
			status.layer = 99
			return status

		if row == "date":
			date = evas.Text(self.canvas, font=("Sans:style=Edje-Vera", 18), color="#808080")
			date.pos = (480/20+50, (640*2)/9+num*640/9+5)
			date.layer = 99
			return date

		if row == "number":
			content = evas.Text(self.canvas, font=("Sans:style=Edje-Vera", 18), color="#808080")
			content.pos = (480/20+50, (640*2)/9+num*640/9+30)
			content.layer = 99
			return content

		if row == "bg":
			bg = evas.Rectangle(self.canvas, pos=(480/20, (640*2)/9+num*640/9+5), size=((480*18)/20, 640/12), color="#38ffffff")
			bg.layer = 99
			bg.on_mouse_up_add(button_callback)
			return bg

	def init_button(self, name, x, y, dx, dy):
		def button_callback(source, event):
			if name == 'back':
				PyneoController.show_dialer_screen()
			elif name == 'next':
				new_offset = self.calls_offset + 5
				if DatabaseController.get_call_count(self.sorted_by_state) > new_offset:
					self.calls_offset = new_offset
					self.show_calls()
			elif name == 'previous':
				new_offset = self.calls_offset - 5
				if new_offset >= 0:
					self.calls_offset = new_offset
					self.show_calls()
			print '--- ', name
		button = evas.Image(self.canvas, pos=(x,y), size=(dx,dy), file="%s%s.png" %(THEME_IMAGES, name))
		button.fill = 0, 0, dx, dy
		button.layer = 99
		button.on_mouse_up_add(button_callback)
		return button

	def del_displayed_calls(self):
		x = 1
		while x < 6:
			self.bg_line[str(x), 'status'].file_set('%sone.png' %THEME_IMAGES)
			self.bg_line[str(x), 'status'].fill = 0, 0, 33, 33
			self.bg_line[str(x), 'date'].text = ""
			self.bg_line[str(x), 'number'].text = ""
			x += 1

	def show_calls(self):
		x = 1
		self.del_displayed_calls()
		self.subheadline.text = ("sorted by: %s" % self.sorted_by_state)
		self.subheadline.pos = ((WIDTH-self.subheadline.horiz_advance)/2, 100)
		if self.sorted_by_state == 'time':
			calls = DatabaseController.get_calls('%', 5, self.calls_offset)
		else:
			calls = DatabaseController.get_calls(self.sorted_by_state, 5, self.calls_offset)

		for i in calls:
			self.bg_line[str(x), 'status'].file_set('%sphone.%s.png' %(THEME_IMAGES,i[0]))
			self.bg_line[str(x), 'status'].fill = 0, 0 ,33, 33
			self.bg_line[str(x), 'date'].text = i[2][:16]
			number = i[1]
			name = DatabaseController.get_name_from_number(i[1])
			print 'name:', name
			if name:
				self.bg_line[str(x), 'number'].text = name
			else:
				self.bg_line[str(x), 'number'].text = number
			x += 1

	def show(self):
		self.bg.show()
		self.headline.show()
		self.subheadline.show()

		for pos, text in enumerate(["back", "previous", "next"]):
			self.buttons[text].show()

		for i, text in enumerate(["1" ,"2", "3", "4", "5"]):
			for j, row in enumerate(["status", "date", "number", "bg"]):
				self.bg_line[text, row].show()

	def hide(self):
		self.bg.hide()
		self.headline.hide()
		self.subheadline.hide()

		for pos, text in enumerate(["back", "previous", "next"]):
			self.buttons[text].hide()

		for i, text in enumerate(["1" ,"2", "3", "4", "5"]):
			for j, row in enumerate(["status", "date", "number", "bg"]):
				self.bg_line[text, row].hide()

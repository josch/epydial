#!/usr/bin/env python2.5
# -*- coding: utf-8 -*-
___author__ = "F. Gau <fgau@pyneo.org>, Thomas 'thomasg' Gstaedtner <thomas (a) gstaedtner (.) net>"
_version__ = "prototype"
__copyright__ = "Copyright (c) 2008"
__license__ = "GPL3"

from epydial import *

class ContactsScreen():
	def register_pyneo_callbacks(self):
		pass

	contact_offset = 0
	detail = False

	def __init__(self, screen_manager):
		self.buttons = {}
		self.bg_line = {}
		self.canvas = screen_manager.get_evas()

		self.bg = evas.Image(self.canvas, pos=(0, 0), size=(WIDTH, HEIGHT), file=PyneoController.set_bg_image)
		self.bg.fill = 0, 0, WIDTH, HEIGHT
		self.bg.layer = 99

		self.headline = evas.Text(self.canvas, text="contacts", font=("Sans:style=Bold,Edje-Vera", 60), color="#808080")
		self.headline.layer = 99
		self.headline.pos = ((WIDTH-self.headline.horiz_advance)/2, 25)

		self.subheadline = evas.Text(self.canvas, font=("Sans,Edje-Vera", 25), color="#808080")
		self.subheadline.layer = 99
		self.subheadline.pos = ((WIDTH-self.subheadline.horiz_advance)/2, 100)

		for pos, text in enumerate(["back", "previous", "next"]):
			self.buttons[text] = self.init_button(text, (pos+1)*16+pos*100, 524, 100, 100)

		for i, text in enumerate(["1" ,"2", "3", "4", "5"]):
			for j, row in enumerate(["lastname", "bg"]):
				self.bg_line[text, row] = self.init_line(row, text, i)

		self.show_contacts()

	def init_line(self, row, name, num):
		def button_callback(source, event):
			if name == '1' or name == '2' or name == '3' or name == '4' or name == '5':
				PyneoController.dialer_text_set(self.bg_line[name, 'lastname'].text.split(',')[1][1:-4])
				PyneoController.show_dialer_screen()
			print '---', name

		if row == "bg":
			bg = evas.Rectangle(self.canvas, pos=(480/20, (640*2)/9+num*640/9+5), size=((480*18)/20, 640/12), color="#38ffffff")
			bg.layer = 99
			bg.on_mouse_up_add(button_callback)
			return bg

		if row == "lastname":
			lastname = evas.Text(self.canvas, font=("Sans:style=Edje-Vera", 28), color="#808080")
			lastname.pos = (480/20+10, (640*2)/9+num*640/9+5)
			lastname.layer = 99
			return lastname

	def init_button(self, name, x, y, dx, dy):
		def button_callback(source, event):
			if name == 'back':
				PyneoController.show_dialer_screen()
			elif name == 'next':
				new_offset = self.contact_offset + 5
				if DatabaseController.get_contact_count() > new_offset:
					self.contact_offset = new_offset
					self.show_contacts()
			elif name == 'previous':
				new_offset = self.contact_offset - 5
				if new_offset >= 0:
					self.contact_offset = new_offset
					self.show_contacts()
			pass
			print '--- ', name
		button = evas.Image(self.canvas, pos=(x,y), size=(dx,dy), file="%s%s.png" % (THEME_IMAGES, name))
		button.fill = 0, 0, dx, dy
		button.layer = 99
		button.on_mouse_up_add(button_callback)
		return button

	def del_displayed_contacts(self):
		x=1
		while x < 6:
			self.bg_line[str(x), 'lastname'].text = ""
			x += 1

	def show_contacts(self):
		x = 1
		self.del_displayed_contacts()
		cursor = DatabaseController.get_contacts(5, self.contact_offset)
		for i in cursor:
			self.bg_line[str(x), 'lastname'].text = '%s, %s ...' % (i[0], i[1])
			x += 1

	def show(self):
		self.bg.show()
		self.headline.show()
		self.subheadline.show()

		for pos, text in enumerate(["back", "previous", "next"]):
			self.buttons[text].show()

		for i, text in enumerate(["1" ,"2", "3", "4", "5"]):
			for j, row in enumerate(["lastname", "bg"]):
				self.bg_line[text, row].show()

	def hide(self):
		self.bg.hide()
		self.headline.hide()
		self.subheadline.hide()

		for pos, text in enumerate(["back", "previous", "next"]):
			self.buttons[text].hide()

		for i, text in enumerate(["1" ,"2", "3", "4", "5"]):
			for j, row in enumerate(["lastname", "bg"]):
				self.bg_line[text, row].hide()

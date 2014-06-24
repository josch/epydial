#!/usr/bin/env python2.5
# -*- coding: utf-8 -*-
__author__ = "Patrick Beck (pbeck (a) yourse (.) de)"
__version__ = "prototype"
__copyright__ = "Copyright (c) 2009"
__license__ = "GPL3"

# TODO
# the description text will not be displayed always - sometimes on the half of the text will be displayed
# you can test it when you go back and forward

from epydial import *

STYLE = """
DEFAULT='font=Sans font_size=18 align=left color=#ffffff wrap=word valign=top'
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

class SimImporter():

        def register_pyneo_callbacks(self):
                pass

	def __init__(self, screen_manager):
		self.FONT_COLOR = PyneoController.set_font_color
		self.red = int(self.FONT_COLOR[3:5], 16)
                self.green = int(self.FONT_COLOR[5:7], 16)
                self.blue = int(self.FONT_COLOR[7:], 16)
                self.alpha = int(self.FONT_COLOR[1:3], 16)

		self.buttons = {}
		self.canvas = screen_manager.get_evas()

		self.bg = evas.Image(self.canvas, pos=(0, 0), size=(WIDTH, HEIGHT), file=PyneoController.set_bg_image)
		self.bg.fill = 0, 0, WIDTH, HEIGHT
		self.bg.layer = 97

		self.headline = evas.Text(self.canvas, text="SIM - Importer", font=("Sans:style=Bold,Edje-Vera", 50), color=self.FONT_COLOR)
		self.headline.layer = 99
		self.headline.pos = ((WIDTH-self.headline.horiz_advance)/2, 25)

		self.description_background = evas.Rectangle(self.canvas, pos=(0,135), size=(480,100), color='#%02x%02x%02x%02x' % (self.alpha/2, self.red, self.green, self.blue))
		self.description_background.layer = 99

		self.description = evas.Textblock(self.canvas, pos=(0,155), size=(480,100), color=self.FONT_COLOR )
		self.description.layer = 99
		text = '%s%s' % ('<center>SIM - Importer synchronize contacts from</center><br>', '<center>your sim-card to your phonebook database</center>')
		self.description.text_markup_set(text)
		self.description.style_set(STYLE)

		self.status = evas.Textblock(self.canvas, pos=(0,480), size=(480,50), )
		self.status.layer = 99
		self.status.style_set(STYLE)

		for pos, text in enumerate(["back"]):
                	self.buttons[text] = self.init_button(text, (pos+1)*16+pos*100, 524, 100, 100)

                self.buttons["sync_button"] = self.init_button("sync_button", 88,300, 303, 120)

	def init_button(self, name, x, y, dx, dy):

		def button_callback(source, event):
			if name == 'sync_button':
                       		self.status.text_markup_set("<center> Syncing started ... </center>")
				self.on_get_phbook()
			elif name == 'back':
				self.status.text_markup_set("")
				PyneoController.show_screen(FONTCOLOR_SCREEN_NAME)
			print name

                button = evas.Image(self.canvas, pos=(x,y), size=(dx,dy), file="%s%s.png" % (THEME_IMAGES, name))
                button.fill = 0, 0, dx, dy
                button.layer = 99
                button.on_mouse_up_add(button_callback)
                return button

	def on_get_phbook(self):
		def error_cb(msg):
			self.status.text_markup_set("<center>Not possible to get the sim contacts</center>") # it's none when a error comes up

		def ok_cb(status):
			contactssim = PyneoController.get_phbook(status)
			self.check_db(contactssim) # when all right, go over to check the database
		PyneoController.get_phbook_raw(ok_cb, error_cb)

        def show(self):
                self.bg.show()
                self.headline.show()
		self.description_background.show()
		self.description.show()
		self.status.show()
                for text in ["sync_button", "back"]:
                        self.buttons[text].show()

        def hide(self):
                self.bg.hide()
                self.headline.hide()
		self.description_background.hide()
		self.description.hide()
		self.status.hide()
                for text in ["sync_button", "back"]:
                        self.buttons[text].hide()

	def check_db(self, contactssim): # check if the contacts already in the database
		print '-----', 'check if the contacts new'
		print '-----', 'Connecting to the database - to read'
		contactsdb = DatabaseController.get_allcontacts()

		newsimcontacts = {}

		for i in contactssim:   # compare the two dicts, if not in database => add it
			if not i in contactsdb:
				newsimcontacts[i] = contactssim[i]

		if not newsimcontacts:
			self.status.text_markup_set("<center>All contacts already in your phonebook</center>")
			print '-----', 'All contacts already in your phonebook'
		else:
			self.sync_with_db(newsimcontacts)

	def sync_with_db(self, newsimcontacts):
		print '-----', 'add the new contacts to the datbase'

		print 'Connecting to the database'
		print 'This contacts are added to the database'

		for key, item in newsimcontacts.iteritems(): # split the dict into name and number
			DatabaseController.insert_contact(item, key) # Databasecontroller to add contacts to the db through epydial
			print  key, ':', item

		self.status.text_markup_set("<center>All new contacts added to the database</center>")

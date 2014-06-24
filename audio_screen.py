#!/usr/bin/env python2.5
# -*- coding: utf-8 -*-
from __future__ import with_statement
__author__ = "M. Dietrich <mdt@pyneo.org>, F. Gau <fgau@pyneo.org>, Thomas Gstaedner (thomas (a) gstaedtner (.) net)"
__version__ = "prototype"
__copyright__ = "Copyright (c) 2009"
__license__ = "GPL3"

from epydial import *

STYLE = """
DEFAULT='font=Sans font_size=18 align=left color=#808080 wrap=word valign=top'
h1='+ font_size=38 font=Bookman'
/h1='- \\n \\n'
p='+ '
/p='- \\n \\n'
br='\\n'
red='+ color=#660000'
/red='-'
center='+ align=center'
/center='-'
right='+ align=right'
/right='-'
big='+ font_size=40'
/big='-'
"""

class AudioScreen():
	toggle = False
	volume = 10

	def register_pyneo_callbacks(self):
		PyneoController.register_callback("on_get_music_tags", self.on_get_music_tags)
		PyneoController.register_callback("on_get_music_position", self.on_get_music_position)

	def __init__(self, screen_manager):
		PyneoController.set_volume(self.volume/100.0)

		self.buttons = {}
		self.canvas = screen_manager.get_evas()

		self.bg = evas.Image(self.canvas, pos=(0, 0), size=(WIDTH, HEIGHT), file=PyneoController.set_bg_image)
		self.bg.fill = 0, 0, WIDTH, HEIGHT
		self.bg.layer = 99

		def headline_callback(source, event):
			if source:
				PyneoController.set_playlist_from_dir(MUSIC_FILE_PATH)
				print 'headline'

		self.headline = evas.Text(self.canvas, text="music", font=("Sans:style=Bold,Edje-Vera", 60), color="#808080")
		self.headline.layer = 99
		self.headline.pos = ((480-self.headline.horiz_advance)/2, 25)
		self.headline.on_mouse_up_add(headline_callback)

		self.cover = evas.Image(self.canvas, pos=(10, 120), size=(160, 155), file="%scover.png" % THEME_IMAGES)
		self.cover.fill = 0, 0, 160, 155
		self.cover.layer = 99

		self.title_tags = evas.Textblock(self.canvas, pos=(190, 130), size=(280, 150), )
		self.title_tags.style_set(STYLE)
		self.title_tags.layer = 99

		self.position_tags = evas.Textblock(self.canvas, pos=(16, 300), size=(448, 150), )
		self.position_tags.style_set(STYLE)
		self.position_tags.layer = 99

		self.bargraph = evas.Rectangle(self.canvas, pos=(16, 336), color="#808080")
		self.bargraph.layer = 99

		self.volume_caption = evas.Text(self.canvas, text="volume %d%%" % self.volume, font=("Sans:style=Bold, Edje-Vera", 18), color="#808080")
		self.volume_caption.layer = 99
		self.volume_caption.pos = ((480-self.volume_caption.horiz_advance)/2, 432)

		for pos, text in enumerate(["back", "previous", "play", "next"]):
			self.buttons[text] = self.init_button(text, (pos+1)*16+pos*100, 524, 100, 100)

		for pos, text in enumerate(["player-minus", "player-plus"]):
			self.buttons[text] = self.init_button(text, (pos+1)*16+pos*332, 400, 100, 100)

	def init_button(self, name, x, y, dx, dy):
		def button_callback(source, event):
			if name == 'back':
				PyneoController.show_screen(AUDIOSORT_SCREEN_NAME)
			elif name == 'next':
				PyneoController.next_music()
			elif name == 'previous':
				PyneoController.previous_music()
			elif name == 'play':
				if not self.toggle:
					self.buttons['play'].file_set('%spause.png' % THEME_IMAGES)
					self.buttons['play'].fill = 0, 0, 100, 100
					PyneoController.play_music()
					PyneoController.get_music_tags()
					self.toggle = True
				elif self.toggle:
					self.buttons['play'].file_set('%splay.png' % THEME_IMAGES)
					self.buttons['play'].fill = 0, 0, 100, 100
					PyneoController.pause_music()
					self.toggle = False
			elif name == 'player-plus' and self.volume < 100:
				self.volume += 10
				PyneoController.set_volume(self.volume/100.0)
				self.volume_caption.text = 'volume %d%%' % self.volume
			elif name == 'player-minus' and self.volume > 0:
				self.volume -= 10
				PyneoController.set_volume(self.volume/100.0)
				self.volume_caption.text = 'volume %d%%' % self.volume
			print '--- ', name
		button = evas.Image(self.canvas, pos=(x,y), size=(dx,dy), file="%s%s.png" % (THEME_IMAGES, name))
		button.fill = 0, 0, dx, dy
		button.layer = 99
		button.on_mouse_up_add(button_callback)
		return button

	def cover_search(self, dir, extension):
		'''searches in a dir for files with a given file extension'''
		path = os.getcwd() # get current path
		os.chdir(dir) # change dir
		searchstring = '*.%s' % extension # create the string for search
		firstfind = glob.glob(searchstring)[0] # get the first image
		os.chdir(path) # change back to the dir before
		return firstfind

	def on_get_cover(self, status):
		'''When a Cover in the music directory exists it will be set'''
		dir = status['file'].rsplit('/', 1)[0] # get the dir path out of the status message with filename
		extensions = ['jpg', 'jpeg', 'png', 'gif'] # file extension for searching
		for i in extensions:

			try:
				cover = self.cover_search(dir, i)
				print '--- set cover %s from dir' % cover
				self.cover.file_set('%s/%s' % (dir, cover))
				self.cover.fill = 0, 0, 160, 160
				break # exit the loop, we need only the first
				return True
			except IndexError:
				print '--- no %s cover found' % i

		return False

	def on_get_amazon_cover(self, status):
		cover_name = '%s_%s' % (status['artist'], status['album'])
		self.cover_path = COVER_FILE_PATH + cover_name
		def update_image(*args):
			self.cover.file_set(self.cover_path.encode("utf8"))
			x, y = self.cover.image_size
			self.cover.fill = 0, 0, 160, 160
		def error(msg):
			print '--- error on cover lookup:', msg

		if not os.path.isfile(self.cover_path):
			print '--- cover in coverdir not exists'
			PyneoController.get_amazon_cover(
				'%s %s' % (status['artist'].encode("utf-8"), status['album'].encode("utf-8")),
				cover_name, update_image, error)
		else:
			print '--- cover exists'
			update_image()

	def on_get_music_position(self, position, duration):
		if position != -1 and duration != -1:
			self.position_tags.text_markup_set('%s<br><br><right>%s</right>' % (
				time.ctime(position)[14:][:5],
				time.ctime(duration)[14:][:5]))
		else:
			self.position_tags.text_markup_set('<center>00:00<br>00:00</center>')
		self.bargraph.size = position*448/duration, 10

	def on_get_music_tags(self, status):
		tag_unknown = False
		for tag in ["artist", "album"]:
			if not tag in status:
				status[tag] = 'unknown %s' % tag
				tag_unknown = True

		if tag_unknown:
			self.cover.file_set('%scover.png' % THEME_IMAGES)
			self.cover.fill = 0, 0, 160, 160
			print '--- set placeholder'

#		if self.on_get_cover(status) == False:
		self.on_get_amazon_cover(status) # get cover from amazon when it exists

		if not 'title' in status: status['title'] = 'unknown title'
		self.title_tags.text_markup_set(('%s<br>%s<br>%s' % (
			status['artist'],
			status['album'],
			status['title'])).encode("utf8"))

	def show(self):
		self.bg.show()
		self.headline.show()
		self.cover.show()
		self.title_tags.show()
		self.position_tags.show()
		self.volume_caption.show()
		self.bargraph.show()
		for text in ["back", "previous", "play", "next", "player-plus", "player-minus"]:
			self.buttons[text].show()

	def hide(self):
		self.bg.hide()
		self.headline.hide()
		self.cover.hide()
		self.title_tags.hide()
		self.position_tags.hide()
		self.volume_caption.hide()
		self.bargraph.hide()
		for text in ["back", "previous", "play", "next", "player-plus", "player-minus"]:
			self.buttons[text].hide()

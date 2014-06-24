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

class GpsStatusScreen():
	def register_pyneo_callbacks(self):
		PyneoController.register_callback("power_status_gps", self.on_power_status_gps)
		PyneoController.register_callback("gps_position_change", self.on_gps_position_change)

	def __init__(self, screen_manager):
		status_track = "off"
		file_track = None
		trackpoints = None
		track_timer = None
		self.buttons = {}
		self.canvas = screen_manager.get_evas()

		self.bg = evas.Image(self.canvas, pos=(0, 0), size=(WIDTH, HEIGHT), file=PyneoController.set_bg_image)
		self.bg.fill = 0, 0, WIDTH, HEIGHT
		self.bg.layer = 99

		self.headline = evas.Text(self.canvas, text="gps status", font=("Sans:style=Bold,Edje-Vera", 60), color="#808080")
		self.headline.layer = 99
		self.headline.pos = ((480-self.headline.horiz_advance)/2, 25)

		self.fix_txt = evas.Text(self.canvas, text="nix fix", font=("Sans:style=Bold,Edje-Vera", 60), color="#808080")
		self.fix_txt.layer = 98
		self.fix_txt.pos =((WIDTH-self.fix_txt.horiz_advance)/2, (HEIGHT-self.fix_txt.vert_advance)/2)

		self.tb_gps = evas.Textblock(self.canvas, pos=(10,110), size=(600,210), )
		self.tb_gps.layer = 99
		self.tb_gps.style_set(STYLE)

		for pos, text in enumerate(["back", "gps_on", "forward"]):
			self.buttons[text] = self.init_button(text, (pos+1)*16+pos*100, 524, 100, 100)

		PyneoController.power_status_gps()

	def init_button(self, name, x, y, dx, dy):
		def button_callback(source, event):
			if name == 'back':
				PyneoController.show_dialer_screen()
			elif name == 'forward':
				PyneoController.show_gps_map_screen()
			elif name == 'gps_on' and self.p_status == 'off':
				PyneoController.power_up_gps()
#				PyneoController.
			elif name == 'gps_on' and self.p_status == 'on':
				PyneoController.power_down_gps()
				self.tb_gps.text_markup_set("")
				self.fix_txt.layer = 98
			print '--- ', name
		button = evas.Image(self.canvas, pos=(x,y), size=(dx,dy), file="%s%s.png" % (THEME_IMAGES, name))
		button.fill = 0, 0, dx, dy
		button.layer = 99
		button.on_mouse_up_add(button_callback)
		return button

	def on_power_status_gps(self, status):
		if status: self.p_status = 'on'
		else: self.p_status = 'off'
		self.buttons['gps_on'].file = '%s/gps_%s.png' % (THEME_IMAGES, self.p_status)

	def on_gps_position_change(self, status):
		if status:
			if status.get('course', 0):
				course = status.get('course', 0)
			else:
				course = 0
			self.fix_txt.layer = 98
			self.tb_gps.text_markup_set("fix: %s<br>long/lat: %0.4f/%0.4f<br>altitude: %0.f<br>kph/course: %0.f/%0.f<br>satellites: %s"
				% (status.get('fix', 0), status.get('longitude', 0), status.get('latitude', 0),
				status.get('altitude', 0), status.get('speed', 0), course, status.get('satellites', 0)))

#			if self.status_track == "on" and status['latitude'] and status['longitude']:
#				self.trackpoints += 1
#				self.track_timer += 1
#				self.file_track.write('%s,%s,%s\n' %(self.trackpoints, status['latitude'], status['longitude']))
#				self.part_text_set("gps_track", "track log: on<br>trackpoints: %s" %self.trackpoints)
#				if self.track_timer == 60:
#					self.file_track.flush()
#					self.track_timer = 0

#		if not status:
		else:
			self.tb_gps.text_markup_set('')
			self.fix_txt.layer = 99

	def start_tracking(self):
		self.status_track = "on"
#		self.part_text_set("gps_track", "track log: on")

		if not os.path.exists(TRACK_FILE_PATH):
			os.mkdir(TRACK_FILE_PATH)
		self.file_track = open(TRACK_FILE_PATH + 'track.log', 'w')
		self.trackpoints = self.track_timer = 0

	def stop_tracking(self):
		self.status_track = "off"
#		self.part_text_set("gps_track", "track log: off")
		self.file_track.close()
		self.trackpoints = self.track_timer = 0

	def show(self):
		self.bg.show()
		self.headline.show()
		self.fix_txt.show()
		self.tb_gps.show()
		for text in ["back", "gps_on", "forward"]:
			self.buttons[text].show()

	def hide(self):
		self.bg.hide()
		self.headline.hide()
		self.fix_txt.hide()
		self.tb_gps.hide()
		for text in ["back", "gps_on", "forward"]:
			self.buttons[text].hide()

#	@edje.decorators.signal_callback("mouse,up,1", "*")
#	def on_edje_signal_dialer_status_triggered(self, emission, source):
#		status = self.part_text_get("button_11_caption")
#		if source == "headline" and self.status_track == "off":
#			self.start_tracking()
#		elif source == "headline" and self.status_track == "on":
#			self.stop_tracking()

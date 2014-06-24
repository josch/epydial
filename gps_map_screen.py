#!/usr/bin/env python
# -*- coding: utf-8 -*-
__author__ = "Johannes 'josch' Schauer <j.schauer@email.de>, M. Dietrich <mdt@pyneo.org>, F. Gau <fgau@pyneo.org>"
__version__ = "prototype"
__copyright__ = "Copyright (c) 2008 J. Schauer, 2008 M. Dietrich"
__license__ = "GPLv3"

from pyneo.codings import decode_json
import re
import evas
from edje import decorators
import math
from epydial import *

class GpsMapScreen():

	def register_pyneo_callbacks(self):
		PyneoController.register_callback("gps_position_change", self.on_gps_position_change)
		PyneoController.register_callback("on_map_new_file", self.on_map_new_file)
		PyneoController.register_callback("on_get_geocoding", self.on_get_geocoding)

	class Tile(evas.Image):
		def __init__(self, canvas):
			evas.Image.__init__(self, canvas)
			self.pass_events = True
			#we need this to store the original position while the zoom animations
			self.position = (0, 0)
			self.size = 256, 256
			self.fill = 0, 0, 256, 256

		def set_position(self, x, y):
			self.position = (x, y)
			self.move(x, y)

	def __init__(self, screen_manager, latitude=0.0, longitude=0.0, zoom=0.0, map_type="OsmStreet"):
		self.canvas = screen_manager.get_evas()

#		self.pass_events = True
#		self.position = (0, 0)
		self.size = 480, 640
#		self.fill = 0, 0, 256, 256

#		def set_position(self, x, y):
#			self.position = (x, y)
#			self.move(x, y)

		self.buttons = {}

		self.config = ConfigParser(INI_PATH).get_section_config('map')
		self.map_type = self.config.get("map_type") or map_type

		self.pymapd_cache = ConfigParser('/etc/pyneod.ini').get_section_config('map').get('cache_directory')
		self.cache_directory = '/'.join([self.pymapd_cache, self.map_type, "%d/%d/%d"])

		#mouse position
		self.x_pos, self.y_pos = (0, 0)

		#global variable for zooming
		self.zoom_step = 0.0

		#initial latitude, longitude, zoom
		self.latitude = latitude or float(self.config.get('latitude'))
		self.longitude = longitude or float(self.config.get('longitude'))
		self.altitude = 0.0
		self.kph = 0.0
		self.course = 0.0
		self.x = 0
		self.y = 0
		self.zoom = zoom or int(self.config.get('zoom'))
		self.offset_x = 0
		self.offset_y = 0

		self.overlay = evas.Text(self.canvas, font=("Sans:style=Bold, Edje-Vera", 24), color="#808080")
		self.overlay_text = "lat:%0.4f lon:%0.4f a:%0.f v:%0.f"
		self.overlay.layer = 2
		self.overlay.on_mouse_up_add(self.on_edje_signal_dialer_status_triggered)

		self.geo_text = evas.Text(self.canvas, font=("Sans:style=Bold, Edje-Vera", 18), color="#808080")
		self.geo_text.layer = 2
		self.geo_text.pos = (0, 30)

		self.pinpoint = evas.Rectangle(self.canvas, pos=(238, 318), size=(4, 4), color="#ff0000")
		self.pinpoint.layer = 2

		self.arrow = evas.Image(self.canvas)
		self.arrow.geometry = 190, 270, 100, 100
		self.arrow.fill = 0, 0, 100, 100
		self.arrow.layer = 2
		self.arrow.pass_events = True

		for pos, text in enumerate(["back", "player-minus", "player-plus", "info"]):
			self.buttons[text] = self.init_button(text, (pos+1)*16+pos*100, 524, 100, 100)

		#calculate size of tile raster
		self.border_x = int(math.ceil(self.size[0]/256.0))
		self.border_y = int(math.ceil(self.size[1]/256.0))

		self.mouse_down = False

		self.animate = False
		self.fix = False

		self.icons = []
		self.init_icons()
		self.set_current_tile(self.latitude, self.longitude, self.zoom)

	def init_button(self, name, x, y, dx, dy):
		def button_callback(source, event):
			if name == 'back':
				PyneoController.show_gps_status_screen()
			elif name == "player-minus" and not self.animate:
				ecore.timer_add(0.05, self.animate_zoom_out)
			elif name == "player-plus" and not self.animate:
				ecore.timer_add(0.05, self.animate_zoom_in)
			elif name == "info":
				PyneoController.get_geocoding(self.latitude, self.longitude)
			print '---', name
		button = evas.Image(self.canvas, pos=(x,y), size=(dx,dy), file="%s%s.png" % (THEME_IMAGES, name))
		button.fill = 0, 0, dx, dy
		button.layer = 2
		button.on_mouse_up_add(button_callback)
		return button

	def on_gps_position_change(self, status):
		if status:
			self.fix = True
			self.altitude = float(status.get('altitude', self.altitude))
			self.kph = float(status.get('speed', self.kph))
			if status.get('course', 0):
				self.course = float(status.get('course', self.course))
				self.arrow.show()
				self.arrow.file_set('/'.join([IMAGE_FILES_PATH, "map", "arrow%02d.png"%(round(self.course/15)%24)]))
			else:
				self.course = 0.0
			if not self.animate:
				self.latitude = float(status.get('latitude', self.latitude))
				self.longitude = float(status.get('longitude', self.longitude))
				self.arrow.file_set('/'.join([IMAGE_FILES_PATH, "map", "arrow%02d.png"%int(self.course/15)]))
				self.set_current_tile(self.latitude, self.longitude, self.zoom)
		else:
			self.fix = False
			self.altitude = 0.0
			self.kph = 0.0
			self.course = 0.0
			self.arrow.hide()
			if not self.animate:
				self.overlay.text = self.overlay_text%(self.latitude, self.longitude, self.altitude, self.kph)

	def on_get_geocoding(self, status):
		address_text = re.findall(r'address.*?\n', status['geo'].encode('utf-8'))
		self.geo_text.text = address_text[0][11:]
#		m = decode_json(status['geo'])
#		for item in m('Placemark'):
#			print 'MMMMMM:', item

	def on_edje_signal_dialer_status_triggered(self, edje, emission, source):
		if source == "label" and not self.animate:
			maps_avail = PyneoController.map_tiles.keys()
			self.map_type = maps_avail[(maps_avail.index(self.map_type)+1)%len(maps_avail)]
			self.cache_directory = '/'.join([self.pymapd_cache, self.map_type, "%d/%d/%d"])
			self.init_redraw()
			print '--- map type: ', self.map_type

	def on_map_new_file(self, d):
		for filename, info in d.items():
			if info.get("state") != "DOWNLOADED":
				print "ERROR", filename, info
			else:
				assert filename.startswith('file://')
				filename = filename[7:]
				parts = filename.split("/")
				x = int(parts[-2])
				y = int(parts[-1])

				for icon in self.not_downloaded_tiles:
					if icon.x == x and icon.y == y:
						icon.file_set(filename)

	def hide(self):
		for icon in self.icons:
			icon.hide()
		self.overlay.hide()
		self.geo_text.hide()
		self.arrow.hide()
		self.pinpoint.hide()
		for text in ["back", "player-plus", "player-minus", "info"]:
			self.buttons[text].hide()
		# when to store current settings permanently?
		# self.config.set('map_type', self.map_type)
		# self.config.set('longitude', self.longitude)
		# self.config.set('latitude', self.latitude)
		# self.config.set('zoom', self.zoom)
		# self.config.config.save()

	def show(self):
		for icon in self.icons:
			icon.show()
		self.overlay.show()
		self.geo_text.show()
		self.pinpoint.show()
		if self.fix:
			self.arrow.show()
		for text in ["back", "player-plus", "player-minus", "info"]:
			self.buttons[text].show()

	#jump to coordinates
	def set_current_tile(self, latitude, longitude, zoom):
		#update shown coordinates everytime they change
		self.overlay.text = self.overlay_text%(latitude, longitude, self.altitude, self.kph)
#		self.overlay.part_text_set("zoom", str(zoom))

		x = (longitude+180)/360 * 2**zoom
		y = (1-math.log(math.tan(latitude*math.pi/180) + 1/math.cos(latitude*math.pi/180))/math.pi)/2 * 2**zoom
		offset_x, offset_y = int((x-int(x))*256), int((y-int(y))*256)
		#only redraw if x, y, zoom, offset_x or offset_y differ from before
		if int(x) != int(self.x) \
		or int(y) != int(self.y) \
		or zoom != self.zoom \
		or offset_x != self.offset_x \
		or offset_y != self.offset_y:
			self.zoom = zoom
			self.x = x
			self.y = y
			self.offset_x, self.offset_y = offset_x, offset_y
			self.init_redraw()

	def init_icons(self):
		#clean up
		for icon in self.icons:
			icon.delete()
		self.icons = []
		#fill
		for i in xrange((2*self.border_x+1)*(2*self.border_y+1)):
			self.icons.append(GpsMapScreen.Tile(self.canvas))

	def init_redraw(self):
		self.not_downloaded_tiles = []
		for i in xrange(2*self.border_x+1):
			for j in xrange(2*self.border_y+1):
				k = (2*self.border_y+1)*i+j
				x = int(self.x)+i-self.border_x
				y = int(self.y)+j-self.border_y
				self.icons[k].x = x
				self.icons[k].y = y
				self.icons[k].set_position((i-self.border_x)*256+self.size[0]/2-self.offset_x, (j-self.border_y)*256+self.size[1]/2-self.offset_y)

				filename = self.cache_directory%(self.zoom, self.x+i-self.border_x, self.y+j-self.border_y)
				if exists(filename):
					self.icons[k].file_set(filename)
				else:
					self.icons[k].file_set('/'.join([IMAGE_FILES_PATH, "map", "404.png"]))
					self.not_downloaded_tiles.append(self.icons[k])
		self.current_pos = (0, 0)

		if self.not_downloaded_tiles:
			PyneoController.map_request_tiles(self.latitude, self.longitude, self.zoom, self.map_type)

	def update_coordinates(self):
		x = int(self.x) + (self.offset_x-self.current_pos[0])/256.0
		y = int(self.y) + (self.offset_y-self.current_pos[1])/256.0
		self.longitude = (x*360)/2**self.zoom-180
		n = math.pi*(1-2*y/2**self.zoom)
		self.latitude = 180/math.pi*math.atan(0.5*(math.exp(n)-math.exp(-n)))
		self.overlay.text = self.overlay_text%(self.latitude, self.longitude, self.altitude, self.kph)
#		self.overlay.part_text_set("zoom", str(self.zoom))

	def zoom_in(self, zoom):
		for icon in self.icons:
			x = (1+zoom)*(icon.position[0]-self.size[0]/2)+self.size[0]/2
			y = (1+zoom)*(icon.position[1]-self.size[1]/2)+self.size[1]/2
			icon.geometry = int(x), int(y), 256+int(256*zoom), 256+int(256*zoom)
			icon.fill = 0, 0, 256+int(256*zoom), 256+int(256*zoom)

	def zoom_out(self, zoom):
		for icon in self.icons:
			x = (1-zoom*0.5)*(icon.position[0]-self.size[0]/2)+self.size[0]/2
			y = (1-zoom*0.5)*(icon.position[1]-self.size[1]/2)+self.size[1]/2
			icon.geometry = int(x), int(y), 256-int(256*zoom*0.5), 256-int(256*zoom*0.5)
			icon.fill = 0, 0, 256-int(256*zoom*0.5), 256-int(256*zoom*0.5)

	def animate_zoom_in(self):
		if self.zoom < 18:
			self.animate = True
			if self.zoom_step < 1.0:
				self.zoom_in(self.zoom_step)
				self.zoom_step+=0.125
				return True

			self.zoom_step = 0.0
			self.set_current_tile(self.latitude, self.longitude, self.zoom+1)
			for icon in self.icons:
				icon.size = 256, 256
				icon.fill = 0, 0, 256, 256
			self.animate = False
		return False

	def animate_zoom_out(self):
		if self.zoom > 5:
			self.animate = True
			if self.zoom_step < 1.0:
				self.zoom_out(self.zoom_step)
				self.zoom_step+=0.125
				return True

			self.zoom_step = 0.0
			self.set_current_tile(self.latitude, self.longitude, self.zoom-1)
			for icon in self.icons:
				icon.size = 256, 256
				icon.fill = 0, 0, 256, 256
			self.animate = False
		return False

	@decorators.signal_callback("mouse,down,1", "*")
	def on_mouse_down(self, emission, source):
		if not self.animate:
			self.x_pos, self.y_pos = self.canvas.pointer_canvas_xy
			self.mouse_down = True

	@decorators.signal_callback("mouse,up,1", "*")
	def on_mouse_up(self, emission, source):
		self.mouse_down = False
		if not self.animate:
			#redraw if moved further than one tile in each direction 'cause the preoload will only download one tile further than requested
			if abs(self.current_pos[0]) > 256 or abs(self.current_pos[1]) > 256:
				self.x = int(self.x) + (self.offset_x-self.current_pos[0])/256.0
				self.y = int(self.y) + (self.offset_y-self.current_pos[1])/256.0
				self.offset_x, self.offset_y = int((self.x-int(self.x))*256), int((self.y-int(self.y))*256)
				self.update_coordinates()
				self.init_redraw()
			if abs(self.current_pos[0]) > 0 or abs(self.current_pos[1]) > 0:
				#on mouse up + move: update current coordinates
				self.update_coordinates()
				if self.not_downloaded_tiles:
					PyneoController.map_request_tiles(self.latitude, self.longitude, self.zoom, self.map_type)

	@decorators.signal_callback("mouse,move", "*")
	def on_mouse_move(self, emission, source):
		if self.mouse_down and not self.animate and not self.fix:
			x_pos, y_pos = self.canvas.pointer_canvas_xy
			delta_x = self.x_pos - x_pos
			delta_y = self.y_pos - y_pos
			self.x_pos, self.y_pos = x_pos, y_pos
			for icon in self.icons:
				icon.set_position(icon.pos[0]-delta_x, icon.pos[1]-delta_y)
			self.current_pos = (self.current_pos[0]-delta_x, self.current_pos[1]-delta_y)
# vim:tw=0:nowrap

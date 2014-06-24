#!/usr/bin/env python2.5
# -*- coding: utf-8 -*-
__author__ = "Soeren Apel (abraxa@dar-clan.de), F. Gau (fgau@pyneo.org), Thomas Gstaedtner (thomas (a) gstaedtner (.) net)"
__version__ = "prototype"
__copyright__ = "Copyright (c) 2008"
__license__ = "GPL3"

from epydial import *

class InfoBarWidget(object):
	def __init__(self, canvas, x, y, w, h, layer):
		FONT_COLOR = PyneoController.get_ini_value('info_bar', 'font_color')
		FONT_STYLE = PyneoController.get_ini_value('info_bar', 'font_style')
		FONT_HEIGHT = int(PyneoController.get_ini_value('info_bar', 'font_height'))
		FONT_BG_COLOR = PyneoController.get_ini_value('info_bar', 'font_bg')

		self.bar_bg = evas.Rectangle(canvas, pos=(x,y), size=(w,h/20), color=FONT_BG_COLOR)
		self.bar_bg.layer = layer

		self.bar_operator = evas.Text(canvas, font=(FONT_STYLE, FONT_HEIGHT), color=FONT_COLOR)
		self.bar_operator.pos = (x+w/80, y)
		self.bar_operator.layer = layer

		self.phone_pix = evas.Image(canvas, size=(16,20))
		self.phone_pix.pos = (self.bar_operator.bottom_right_get()[0]+10, y+5)
		self.phone_pix.layer = layer

		self.sms_pix = evas.Image(canvas, size=(20,14))
		self.sms_pix.pos = (self.bar_operator.bottom_right_get()[0]+30, y+9)
		self.sms_pix.layer = layer

		self.bar_time = evas.Text(canvas, font=(FONT_STYLE, FONT_HEIGHT), color=FONT_COLOR)
		self.bar_time.layer = layer

		self.bar_rssi_bat = evas.Text(canvas, font=(FONT_STYLE, FONT_HEIGHT), color=FONT_COLOR)
		self.bar_rssi_bat.layer = layer

	def show(self):
		self.bar_bg.show()
		self.bar_operator.show()
		self.bar_time.show()
		self.bar_rssi_bat.show()

	def hide(self):
		self.bar_bg.hide()
		self.bar_operator.hide()
		self.bar_time.hide()
		self.bar_rssi_bat.hide()

class Button(evas.Rectangle):
	def __init__(self, coords, *args, **kwargs):
		super(Button, self).__init__(*args, **kwargs)
		self.coords = coords

class TextCaption(object):
	def __init__(self, canvas, x, y, text, caption):
		FONT_COLOR = PyneoController.set_font_color

		self.label = evas.Text(canvas, text=text, font=("Sans:style=Bold,Edje-Vera", 50), color=FONT_COLOR)
		self.label.layer = 3
		self.label.pass_events = True
		self.label.pos = (x*480/3+(480/3-self.label.horiz_advance)/2, 200+y*440/4+(440/4-self.label.vert_advance)/2)
		self.caption = evas.Text(canvas, text=caption, font=("Sans", 20), color=FONT_COLOR)
		self.caption.layer = 3
		self.caption.pass_events = True
		self.caption.pos = (x*480/3+(480/3-self.label.horiz_advance)/2, 200+(y+1)*440/4-self.label.vert_advance/2)

	def show(self):
		self.label.show()
		self.caption.show()

	def hide(self):
		self.label.hide()
		self.caption.hide()

class TextScrollWidget(object):
	def __init__(self, canvas, x=0, y=0, w=0, h=0, layer=0, text="", click_handler=None):
		FONT_COLOR = PyneoController.set_font_color

		self.pos = (x, y)
		self.size = (w, h)
		self.layer = layer
		self.click_handler = click_handler

		self.bg = evas.Rectangle(canvas, pos=self.pos, size=self.size, color="#00FFFFFF")
		self.bg.layer = self.layer
		self.bg.on_mouse_down_add(self.on_mouse_down)
		self.bg.on_mouse_move_add(self.on_mouse_move)
		self.bg.on_mouse_up_add(self.on_mouse_up)

		self.clip = evas.Rectangle(canvas, pos=self.pos, size=self.size, color="#FFFFFF")
		self.clip.layer = self.layer

		self.label = evas.Text(canvas, text=text, font=("Sans:style=Bold,Edje-Vera", 50), color=FONT_COLOR)
		self.label_y = y+(h-self.label.vert_advance)/2
		self.label.pos = x, self.label_y
		self.label.layer = self.layer
		self.label.clip_set(self.clip)
		self.label.pass_events = True
		self.label.show()
		self.mouse = 0
		self.start = 0
		self.mouse_down = False

	def get_text(self):
		# label.text is None when Empty - not ""
		if self.label.text:
			return self.label.text
		else:
			return ""

	def set_text(self, value):
		self.label.text = value
		self.scroll_to_index(len(value))

	text = property(fget=get_text, fset=set_text)

	def on_mouse_down(self, source, event):
		self.mouse_down = True
		self.mouse = self.start = event.position.output[0]
		self.text_x, y = self.label.pos
		ecore.timer_add(0.3, self.on_click)

	def on_click(self):
		if not self.mouse_down:
#		if not self.mouse_down and self.start-7 < self.mouse < self.start+7:
			self.click_handler()

	def on_mouse_move(self, source, event):
		self.mouse = pos = event.position.output[0]
		if self.mouse_down:
			cw, ch = self.size
			cx, cy = self.pos
			pos = -self.text_x+cw+cx-pos+self.start
			if 0 < pos:
				horiz_advance = self.label.horiz_advance
				if pos > horiz_advance:
					self.label.pos = (cw+cx-horiz_advance, self.label_y)
				else:
					r = self.label.char_coords_get(pos, 0)
					if r is not None:
						pos, x, y, w, h = r
						self.label.pos = (cw+cx-x, self.label_y)

	def on_mouse_up(self, source, event):
		self.mouse_down = False

	def show(self):
		self.clip.show()
		self.bg.show()

	def hide(self):
		self.clip.hide()
		self.bg.hide()

	def scroll_to_index(self, index):
		"""index might be out of bound - in this case it is scrolled to the end
		"""
		cw, ch = self.size
		cx, cy = self.pos
		if 0 <= index < len(self.text):
			x, y, w, h = self.label.char_pos_get(index)
		else:
			x = self.label.horiz_advance
		self.label.pos = (cw+cx-x, self.label_y)

	def current_index_get(self):
		"""returns the position of the char that begins at the last char that
		can be seen in the clip or when the last char is already at the end
		then return the length
		"""
		text_x, y = self.label.pos
		cw, ch = self.size
		cx, cy = self.pos
		ret = self.label.char_coords_get(-text_x+cw+cx, 0)
		if ret is not None:
			pos, x, y, w, h = ret
			return ord(pos)+1 # workaround for a small bug index != current_index_get(char_pos_get(index))
		else:
			return len(self.text)

	def delete_current_char(self):
		text = self.text
		index = self.current_index_get()
		self.label.text = text[:index-1]+text[index:]
		cw, ch = self.size
		self.scroll_to_index(index-1)

	def insert_at_current_index(self, ch):
		text = self.text
		index = self.current_index_get()
		self.label.text = text[:index]+ch+text[index:]
		cw, ch = self.size
		self.scroll_to_index(index+1)

class DialWidget(object):
	caption_text = {
		(0,0):".,?!",(1,0):"abc",(2,0):"def",
		(0,1):"ghi",(1,1):"jklm",(2,1):"nop",
		(0,2):"qrs",(1,2):"tuvw",(2,2):"xyz",
		(0,3):"+-/%",(1,3):"\\~[{",(2,3):"@&\"$",
	}
	label_text = [{
		(0,0):"1",(1,0):"2",(2,0):"3",
		(0,1):"4",(1,1):"5",(2,1):"6",
		(0,2):"7",(1,2):"8",(2,2):"9",
		(0,3):"*",(1,3):"0",(2,3):"#",
	},
	{
		(0,0):"1",(1,0):"?",(2,0):"'",
		(0,1):".",(1,1):",",(2,1):":",
		(0,2):"!",(1,2):"`",(2,2):"_",
		(0,3):"",(1,3):"",(2,3):"",
	},
	{
		(0,0):"a",(1,0):"2",(2,0):"c",
		(0,1):"A",(1,1):"b",(2,1):"C",
		(0,2):"",(1,2):"B",(2,2):"",
		(0,3):"",(1,3):"",(2,3):"",
	},
	{
		(0,0):"D",(1,0):"d",(2,0):"3",
		(0,1):"E",(1,1):"e",(2,1):"f",
		(0,2):"",(1,2):"",(2,2):"F",
		(0,3):"",(1,3):"",(2,3):"",
	},
	{
		(0,0):"i",(1,0):"I",(2,0):"",
		(0,1):"4",(1,1):"h",(2,1):"H",
		(0,2):"g",(1,2):"G",(2,2):"",
		(0,3):"",(1,3):"",(2,3):"",
	},
	{
		(0,0):"M",(1,0):"m",(2,0):"L",
		(0,1):"j",(1,1):"5",(2,1):"l",
		(0,2):"J",(1,2):"k",(2,2):"K",
		(0,3):"",(1,3):"",(2,3):"",
	},
	{
		(0,0):"",(1,0):"N",(2,0):"n",
		(0,1):"O",(1,1):"o",(2,1):"6",
		(0,2):"",(1,2):"P",(2,2):"p",
		(0,3):"",(1,3):"",(2,3):"",
	},
	{
		(0,0):"",(1,0):"",(2,0):"",
		(0,1):"s",(1,1):"S",(2,1):"",
		(0,2):"7",(1,2):"r",(2,2):"R",
		(0,3):"q",(1,3):"Q",(2,3):"",
	},
	{
		(0,0):"",(1,0):"",(2,0):"",
		(0,1):"W",(1,1):"w",(2,1):"V",
		(0,2):"t",(1,2):"8",(2,2):"v",
		(0,3):"T",(1,3):"u",(2,3):"U",
	},
	{
		(0,0):"",(1,0):"",(2,0):"",
		(0,1):"",(1,1):"X",(2,1):"x",
		(0,2):"Y",(1,2):"y",(2,2):"9",
		(0,3):"",(1,3):"Z",(2,3):"z",
	},
	{
		(0,0):"",(1,0):"",(2,0):"",
		(0,1):"/",(1,1):"+",(2,1):"|",
		(0,2):"(",(1,2):")",(2,2):"%",
		(0,3):"*",(1,3):"-",(2,3):";",
	},
	{
		(0,0):"",(1,0):"",(2,0):"",
		(0,1):"{",(1,1):"}",(2,1):"\\",
		(0,2):"[",(1,2):"]",(2,2):"\n",
		(0,3):"~",(1,3):"0",(2,3):" ",
	},
	{
		(0,0):"",(1,0):"",(2,0):"",
		(0,1):"^",(1,1):"\"",(2,1):"&",
		(0,2):"@",(1,2):"<",(2,2):">",
		(0,3):"$",(1,3):"=",(2,3):"#",
	}]

	def __init__(self, canvas, click_handler):
		FONT_COLOR = PyneoController.set_font_color

		self.click_handler = click_handler

		# create labels
		self.labelsets = [dict() for i in self.label_text]
		for y in range(4):
			for x in range(3):
				self.labelsets[0][(x,y)] = TextCaption(canvas, x, y, self.label_text[0][(x,y)], self.caption_text[(x,y)])
		for i, labelset in enumerate(self.label_text[1:]):
			for y in range(4):
				for x in range(3):
					label = evas.Text(canvas, text=labelset[(x,y)], font=("Sans:style=Bold,Edje-Vera", 50), color=FONT_COLOR)
					label.layer = 3
					label.pass_events = True
					label.pos = (x*480/3+(480/3-label.horiz_advance)/2, 200+y*440/4+(440/4-label.vert_advance)/2)
					self.labelsets[i+1][(x,y)] = label
		# show the default labelset
		self.current_layer=0
		for label in self.labelsets[self.current_layer].values():
			label.show()

		# create clickbuttons
		self.buttons = dict()
		for y in range(4):
			for x in range(3):
				button = Button((x,y), canvas, pos=(x*480/3,200+y*440/4), size=(480/3,440/4), color="#00000000")
				button.layer = 2
				button.pointer_mode_set(evas.EVAS_OBJECT_POINTER_MODE_NOGRAB)
				button.on_mouse_down_add(self.on_mouse_down)
				button.on_mouse_up_add(self.on_mouse_up)
				button.on_mouse_in_add(self.on_mouse_in)
				button.on_mouse_out_add(self.on_mouse_out)
				button.show()
				self.buttons[(x,y)] = button

		# create color rects
		self.color_buttons = dict()
		for y in range(4):
			for x in range(3):
				button = Button((x,y), canvas, pos=(x*480/3,200+y*440/4), size=(480/3,440/4), color="#222222")
				button.layer = 1
				self.color_buttons[(x,y)] = button

	def on_mouse_down(self, source, event):
		for label in self.labelsets[self.current_layer].values():
			label.hide()
		x, y = source.coords
		self.current_layer = y*3+x+1
		for label in self.labelsets[self.current_layer].values():
			label.show()
		self.color_buttons[source.coords].show()

	def on_mouse_up(self, source, event):
		x, y = source.coords
		letter = self.label_text[self.current_layer][(x,y)]
		self.click_handler(letter)
		for label in self.labelsets[self.current_layer].values():
			label.hide()
		self.current_layer = 0
		for label in self.labelsets[self.current_layer].values():
			label.show()
		self.color_buttons[source.coords].hide()

	def on_mouse_in(self, source, event):
		self.color_buttons[source.coords].show()

	def on_mouse_out(self, source, event):
		self.color_buttons[source.coords].hide()

	def hide(self):
		for label in self.labelsets[self.current_layer].values():
			label.hide()
		for button in self.buttons.values():
			button.hide()

	def show(self):
		for label in self.labelsets[self.current_layer].values():
			label.show()
		for button in self.buttons.values():
			button.show()

class BackspaceButton(evas.Image):
	def __init__(self, canvas, x, y, w, h, click_handler, hold_handler=None):
		evas.Image.__init__(self, canvas, pos=(x, y), size=(w, h), file="/usr/share/epydial/data/themes_data/blackwhite/images/back.png")
		self.fill = 0, 0, w, h
		self.layer = 99
		self.on_mouse_up_add(click_handler)

class DialerScreen():
	number_regex = re.compile("^\+?\d+$")
	text = None

	def __init__(self, screen_manager):
		canvas = screen_manager.get_evas()
		self.text = ""
		self.enter_sim_key = False
		self.look_screen = False
		self.rssi = 0

		self.info_bar = InfoBarWidget(canvas, 0, 0, WIDTH, HEIGHT, 99, )
		self.dial_input = DialWidget(canvas, click_handler=self.on_dialer_click)
		self.backspace_button = BackspaceButton(canvas, 400, 50, 80, 80, click_handler=self.on_backspace)
		self.numberdisplay_text = TextScrollWidget(canvas, 0, 40, 400, 160, click_handler=self.on_dial)
		self.numberdisplay_text.show()
		ecore.timer_add(10, self.display_time)
		self.display_time()

		self.bg = evas.Image(canvas, pos=(0, 0), size=(WIDTH, HEIGHT), file=PyneoController.set_bg_image)
		self.bg.fill = 0, 0, WIDTH, HEIGHT
		self.bg.layer = -10

	def hide(self):
		self.bg.hide()
		self.info_bar.hide()
		self.dial_input.hide()
		self.backspace_button.hide()
		self.numberdisplay_text.hide()

	def show(self):
		self.bg.show()
		self.info_bar.show()
		self.dial_input.show()
		self.backspace_button.show()
		self.numberdisplay_text.show()

	def register_pyneo_callbacks(self):
		PyneoController.register_callback("sim_key_required", self.on_sim_key_required)
		PyneoController.register_callback("sim_ready", self.on_sim_ready)
		PyneoController.register_callback("gsm_registering", self.on_gsm_registering)
		PyneoController.register_callback("gsm_operator_change", self.on_gsm_operator_change)
		PyneoController.register_callback("gsm_signal_strength_change", self.on_gsm_signal_strength_change)
		PyneoController.register_callback("capacity_change", self.on_capacity_change)
		PyneoController.register_callback("dialer_text_set", self.on_text_set)
		PyneoController.register_callback("set_missed_call_icon", self.on_set_missed_call_icon)
		PyneoController.register_callback("set_missed_sms_icon", self.on_set_missed_sms_icon)

	def on_set_missed_call_icon(self, status):
		if status == 'true':
			self.info_bar.phone_pix.file = "%sphone.png" % THEME_IMAGES
		else:
			self.info_bar.phone_pix.file = "%sone.png" % THEME_IMAGES
		self.info_bar.phone_pix.fill = 0, 0, 16, 20
		self.info_bar.phone_pix.show()

	def on_set_missed_sms_icon(self, status):
		if status == 'true':
			self.info_bar.sms_pix.file = "%ssms.png" % THEME_IMAGES
		else:
			self.info_bar.sms_pix.file = "%sone.png" % THEME_IMAGES
		self.info_bar.sms_pix.fill = 0, 0, 20, 14
		self.info_bar.sms_pix.show()

	def on_text_set(self, text):
		self.text = text
		self.numberdisplay_text.text = self.text

	def on_sim_key_required(self, key_type):
		print '---', 'opening keyring'
		self.numberdisplay_text.text = "Enter " + key_type
		self.enter_sim_key = True

	def on_sim_ready(self):
		print '---', 'SIM unlocked'
#		self.numberdisplay_text.text = "SIM unlocked"
		self.text = ""
		self.enter_sim_key = False

	def on_gsm_registering(self):
		self.numberdisplay_text.text = "Registering ..."

	def on_gsm_operator_change(self, operator):
		if (self.numberdisplay_text.text == "Registering ..."):
			self.numberdisplay_text.text = ""
		self.info_bar.bar_operator.text = operator
		self.info_bar.bar_operator.pos = (WIDTH/80, 0)
		self.info_bar.phone_pix.pos = (self.info_bar.bar_operator.bottom_right_get()[0]+10, 5)
		self.info_bar.sms_pix.pos = (self.info_bar.bar_operator.bottom_right_get()[0]+30, 9)

	def on_capacity_change(self, status):
		if status['capacity']:
			self.capacity = status['capacity']
			self.info_bar.bar_rssi_bat.text = "%sdBm / %s%%" % (self.rssi, self.capacity)
			self.info_bar.bar_rssi_bat.pos = (480-self.info_bar.bar_rssi_bat.horiz_advance-480/80, 0)
		else:
			self.capacity = None

	def on_gsm_signal_strength_change(self, rssi):
		self.rssi = rssi
		try:
			self.info_bar.bar_rssi_bat.text	= "%s dBm / %s%%" % (self.rssi, self.capacity)
			self.info_bar.bar_rssi_bat.pos = (480-self.info_bar.bar_rssi_bat.horiz_advance-480/80, 0)
		except: pass

	def display_time(self):
		now = datetime.now()
		self.info_bar.bar_time.text = now.strftime('%H:%M')
		self.info_bar.bar_time.pos = ((WIDTH-self.info_bar.bar_time.horiz_advance)/2, 0)
		return True

	def on_backspace(self, source, event):
		self.numberdisplay_text.delete_current_char()
		self.text = self.numberdisplay_text.text
		print self.text

	def on_dialer_click(self, letter):
		if (self.enter_sim_key & (self.numberdisplay_text.text[:5] == "Enter")):
			self.numberdisplay_text.text = ""
		self.numberdisplay_text.insert_at_current_index(letter)
		self.text = self.numberdisplay_text.text
		print self.text

	def on_dial(self):
		if PyneoController.gsm_sim_locked():
			print '---', 'send pin'
			self.numberdisplay_text.text = "Verifying ..."
			PyneoController.gsm_unlock_sim(self.text)
		elif self.text == "":
			print "--- nothing entered"
		elif self.text == "#":
			print '--- Lock'
			self.text = ""
			self.numberdisplay_text.text = ""
			PyneoController.show_lock_screen()
		elif self.text == "*":
			print '--- Settings Screen'
			self.text = ""
			self.numberdisplay_text.text = ""
			PyneoController.show_screen(SETTINGS_SCREEN_NAME)
		elif len(self.text) <= 2:
			num = int(self.text)
			if num == 1:
				print '--- Gsm Status'
				self.text = ""
				self.numberdisplay_text.text = ""
				PyneoController.show_screen(GSM_STATUS_SCREEN_NAME)
			elif num == 2:
				print '--- Gps Status'
				self.text = ""
				self.numberdisplay_text.text = ""
				PyneoController.show_gps_status_screen()
			elif num == 3:
				print '--- Time Screen'
				self.text = ""
				self.numberdisplay_text.text = ""
#				PyneoController.show_screen(TIME_SCREEN_NAME)
			elif num == 4:
				print '--- Pix'
				self.text = ""
				self.numberdisplay_text.text = ""
				PyneoController.show_screen(PIX_SCREEN_NAME)
			elif num == 5:
				print '--- Yahoo Weather Screen'
				self.text = ""
				self.numberdisplay_text.text = ""
				PyneoController.show_screen(WEATHER_SCREEN_NAME)
			elif num == 6:
				print '--- Hon Screen'
				self.text = ""
				self.numberdisplay_text.text = ""
				PyneoController.show_screen(HON_SCREEN_NAME)
			elif num == 7:
				print '--- Contacts Screen'
				self.text = ""
				self.numberdisplay_text.text = ""
				PyneoController.show_screen(CONTACTS_SCREEN_NAME)
			elif num == 8:
				print '--- Sms Screen'
				self.text = ""
				self.numberdisplay_text.text = ""
				PyneoController.show_screen(SMS_SCREEN_NAME)
			elif num == 9:
				print '--- Audio Screen'
				self.text = ""
				self.numberdisplay_text.text = ""
				PyneoController.show_screen(AUDIOSORT_SCREEN_NAME)
			elif num == 0:
				print '--- Call History Screen'
				self.text = ""
				self.numberdisplay_text.text = ""
				PyneoController.show_screen(HISTORY_SCREEN_NAME)
			elif num == 10:
				print '--- Timetable Screen'
				self.text = ""
				self.numberdisplay_text.text = ""
				PyneoController.show_screen(TIMETABLE_SCREEN_NAME)
			elif num == 11:
				print '--- Wlan Screen'
				self.text = ""
				self.numberdisplay_text.text = ""
				PyneoController.show_screen(WLAN_SCREEN_NAME)
			elif num == 12:
				print '--- Font Color Screen'
				self.text = ""
				self.numberdisplay_text.text = ""
				PyneoController.show_screen(FONTCOLOR_SCREEN_NAME)
			elif num == 13:
				print '--- News Screen'
				self.text = ""
				self.numberdisplay_text.text = ""
				PyneoController.show_screen(NEWS_SCREEN_NAME)
		else:
			tokens = self.text.split(" ")
			if len(tokens) == 1:
				expression = tokens[0]
				number = DatabaseController.get_number_from_name(expression)
				if number:
					PyneoController.show_incall_screen('outgoing')
					PyneoController.gsm_dial(number)
				elif re.match(self.number_regex, self.text):
					PyneoController.show_incall_screen('outgoing')
					PyneoController.gsm_dial(self.text)
				else:
					from math import *
					result = str(eval(expression))
					self.text = result
					self.numberdisplay_text.text = result
					print "%s = %s"%(expression, result)
			elif len(tokens) == 2:
				number, name = tokens
				DatabaseController.insert_contact(number, name)
				self.text = ""
				self.numberdisplay_text.text = ""
			else:
				print "longer token"

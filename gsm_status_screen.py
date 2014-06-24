#!/usr/bin/env python2.5
# -*- coding: utf-8 -*-
__author__ = "Soeren Apel (abraxa@dar-clan.de), F. Gau (fgau@pyneo.org), Thomas Gstaedner (thomas (a) gstaedtner (.) net)"
__version__ = "prototype"
__copyright__ = "Copyright (c) 2008"
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
big='+ font_size=40'
/big='-'
"""

class GsmStatusScreen():

	def register_pyneo_callbacks(self):
		PyneoController.register_callback("power_status_gsm", self.on_power_status_gsm)
		PyneoController.register_callback("device_status", self.on_device_status)
		PyneoController.register_callback("gsm_details", self.on_gsm_details)
		PyneoController.register_callback("gprs_status", self.on_gprs_status)

		PyneoController.get_device_status()
		PyneoController.gsm_details()
		PyneoController.get_gprs_status()
		PyneoController.power_status_gsm()

	def __init__(self, screen_manager):
		self.buttons = {}
		self.canvas = screen_manager.get_evas()

		self.bg = evas.Image(self.canvas, pos=(0, 0), size=(WIDTH, HEIGHT), file=PyneoController.set_bg_image)
		self.bg.fill = 0, 0, WIDTH, HEIGHT
		self.bg.layer = 99

		def headline_callback(source, event):
			if source:
				print '--- start scanning'
				self.headline.text = 'scanning'
				self.headline.pos = ((WIDTH-self.headline.horiz_advance)/2, 25)
				self.on_scan_operator()

		self.headline = evas.Text(self.canvas, text="gsm status", font=("Sans:style=Bold,Edje-Vera", 60), color="#808080")
		self.headline.layer = 99
		self.headline.pos = ((WIDTH-self.headline.horiz_advance)/2, 25)
		self.headline.on_mouse_up_add(headline_callback)

		self.tb_device = evas.Textblock(self.canvas, pos=(10, 110), size=(460, 200), )
		self.tb_device.layer = 99
		self.tb_device.style_set(STYLE)

		self.tb_operator = evas.Textblock(self.canvas, pos=(10, 330), size=(230, 200), )
		self.tb_operator.layer = 99
		self.tb_operator.style_set(STYLE)

		self.tb_gsm_status = evas.Textblock(self.canvas, pos=(240, 330), size=(230, 200), )
		self.tb_gsm_status.layer = 99
		self.tb_gsm_status.style_set(STYLE)

		for pos, text in enumerate(["back", "network.usb", "network.gprs.on", "power.on"]):
			self.buttons[text] = self.init_button(text, (pos+1)*16+pos*100, 524, 100, 100)

	def init_button(self, name, x, y, dx, dy):
		self.p_status = 'on'
		self.g_status = 'off'

		def button_callback(source, event):
			if name == 'back':
				PyneoController.show_dialer_screen()
			elif name == 'power.on' and self.p_status == 'on':
				PyneoController.power_down_gsm()
				print '--- ', name, self.p_status
			elif name == 'power.on' and self.p_status == 'off':
				PyneoController.power_up_gsm()
				print '--- ', name, self.p_status
			elif name == 'network.usb':
				pass
			elif name == 'network.gprs.on' and self.g_status == 'off':
				PyneoController.activate_gprs()
				print '--- ', name, self.g_status
			elif name == 'network.gprs.on' and self.g_status == 'on':
				PyneoController.deactivate_gprs()
				print '--- ', name, self.g_status
		button = evas.Image(self.canvas, pos=(x,y), size=(dx,dy), file="%s%s.png" % (THEME_IMAGES, name))
		button.fill = 0, 0, dx, dy
		button.layer = 99
		button.on_mouse_up_add(button_callback)
		return button

	def show(self):
		self.bg.show()
		self.headline.show()
		self.tb_device.show()
		self.tb_operator.show()
		self.tb_gsm_status.show()
		for text in ["back", "network.usb", "network.gprs.on", "power.on"]:
			self.buttons[text].show()

	def hide(self):
		self.bg.hide()
		self.headline.hide()
		self.tb_device.hide()
		self.tb_operator.hide()
		self.tb_gsm_status.hide()
		for text in ["back", "network.usb", "network.gprs.on", "power.on"]:
			self.buttons[text].hide()

	def on_gprs_status(self, status):
		if status: self.g_status = 'on'
		else: self.g_status = 'off'
		print '--- gprs is ', self.g_status
		self.buttons['network.gprs.on'].file = '%snetwork.gprs.%s.png' % (THEME_IMAGES, self.g_status)
#		status = status.get("device", "off")
#		print '--- network device is ', status
#		self.part_text_set("button_13_caption", status)

	def on_scan_operator(self):
		def error_cb(msg):
			print "error:", msg

		def ok_cb(status):
			operator = 'scan operator:<br>'
			for n, v in status.items():
				operator += v['oper'] + '<br>'
				print 'provider', n, ':', v['oper']
			self.headline.text = "gsm status"
			self.headline.pos = ((WIDTH-self.headline.horiz_advance)/2, 25)
			self.tb_operator.text_markup_set(operator)

		PyneoController.scan_operator(ok_cb, error_cb)

	def on_device_status(self, status):
		self.tb_device.text_markup_set(
			"imei: %s<br>model: %s<br>revision: %s<br>manufacturer: %s" % (
			status['imei'],
			status['model'],
			status['revision'],
			status['manufacturer']))

	def on_gsm_details(self, status):
		self.tb_gsm_status.text_markup_set(
			"operator: %s<br>rssi: %s<br>lac/ci: %s/%s<br>mcc/cc: %s/%s<br>country: %s" % (
			status['oper'],
			status['rssi'],
			status['lac'],
			status['ci'],
			status['mcc'],
			status['cc'],
			status['country']))

	def on_power_status_gsm(self, status):
		if status: self.p_status = 'on'
		else: self.p_status = 'off'
		print '--- gsm device is ', self.p_status
		self.buttons['power.on'].file = '%spower.%s.png' % (THEME_IMAGES, self.p_status)

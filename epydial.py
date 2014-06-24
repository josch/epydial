#!/usr/bin/env python2.5
# -*- coding: utf-8 -*-
__author__ = ', '.join((
	"Soeren Apel (abraxa@dar-clan.de)",
	"Frank Gau (fgau@pyneo.org)",
	"Thomas Gstaedtner (thomas (a) gstaedtner (.) net)",
	"Johannes 'josch' Schauer <j.schauer@email.de>",
	))
__version__ = "prototype"
__copyright__ = "Copyright (c) 2008-2010"
__license__ = "GPLv3"

from dbus import SystemBus
from os.path import exists, isfile
from os import mkdir, unlink, listdir
from datetime import datetime

from e_dbus import DBusEcoreMainLoop
import ecore
import ecore.evas
import evas
import edje

from pyneo.dbus_support import *
from pyneo.sys_support import pr_set_name
from pyneo.cfg_support import ConfigParser

from ConfigParser import SafeConfigParser
from db_support import DatabaseController
from db_init import DatabaseInit
from constants import WIDTH, HEIGHT, FRAMETIME, IMAGE_CACHE_SIZE, FONT_CACHE_SIZE, FULLSCREEN, APP_TITLE, WM_INFO, BASE_PATH, PIX_FILE_PATH, TRACK_FILE_PATH, DB_FILE_PATH, DB_PATH, PIX_WEATHER_FILE_PATH, MUSIC_FILE_PATH, COVER_FILE_PATH, RINGTONE_FILE, SMSTONE_FILE, ALSA_FILES_PATH, IMAGE_FILES_PATH, THEME_IMAGES, INI_PATH, DIALER_SCREEN_NAME, INFO_BAR_WIDGET, INCALL_SCREEN_NAME, GSM_STATUS_SCREEN_NAME, GPS_STATUS_SCREEN_NAME, GPS_MAP_SCREEN_NAME, TIME_SCREEN_NAME, HON_SCREEN_NAME, LOCK_SCREEN_NAME, PIX_SCREEN_NAME, CONTACTS_SCREEN_NAME, SMS_SCREEN_NAME, SMS_DETAIL_SCREEN_NAME, WEATHER_SCREEN_NAME, AUDIO_SCREEN_NAME, AUDIOSORT_SCREEN_NAME, HISTORY_SCREEN_NAME, SETTINGS_SCREEN_NAME, TIMETABLE_SCREEN_NAME, SIMIMPORTER_SCREEN_NAME, WLAN_SCREEN_NAME, FONTCOLOR_SCREEN_NAME, NEWS_SCREEN_NAME


class PyneoController(object):
	_dbus_timer = None
	_gsm_timer = None
	_keyring_timer = None
	_gps_timer = None
	_hon_timer = None
	_callbacks = {}
	_calls = {}

	gsm = None
	pwr = None
	sys = None
	gps = None
	hon = None
	music = None
	gsm_wireless = None
	gsm_keyring = None
	gsm_sms = None
	gsm_contacts = None
	hon_hotornot = None
	ama = None

	gsm_wireless_status = None
	gsm_keyring_status = None

	call_type = None

	call = None
	callsigs = []

	@classmethod
	def register_callback(class_, event_name, callback):
		print "In register_callback: ", event_name
		if class_._callbacks.get(event_name, None):
			class_._callbacks[event_name].append(callback)
		else:
			class_._callbacks[event_name] = [callback]

	@classmethod
	def notify_callbacks(class_, event_name, *args):
		for cb in class_._callbacks.get(event_name, ()):
			cb(*args)

	@classmethod
	def init(class_):
		try:
			class_.gsm = object_by_url('dbus:///org/pyneo/GsmDevice')
			class_.gprs = object_by_url('dbus:///org/pyneo/net/Gprs')
			class_.pwr = object_by_url('dbus:///org/pyneo/System')
			class_.sys = object_by_url(class_.pwr.GetDevice('system', dbus_interface=DIN_POWERED))
			class_.gps = object_by_url('dbus:///org/pyneo/GpsLocation')
			class_.hon = object_by_url('dbus:///org/pyneo/HotOrNot')
			class_.music = object_by_url('dbus:///org/pyneo/Music')
			class_.ama = object_by_url('dbus:///org/pyneo/Amazon')
			class_.map_tiles = {
				'OsmStreet':object_by_url('dbus:///org/pyneo/mapper/OsmStreet'),
				'OsmCycle':object_by_url('dbus:///org/pyneo/mapper/OsmCycle'),
				'OsmTilesathome':object_by_url('dbus:///org/pyneo/mapper/OsmTilesathome'),
				'CloudmadeMidnight':object_by_url('dbus:///org/pyneo/mapper/CloudmadeMidnight'),
				'OPNV':object_by_url('dbus:///org/pyneo/mapper/OPNV'),
				'GoogleMoon':object_by_url('dbus:///org/pyneo/mapper/GoogleMoon'),
			}
			class_.map = object_by_url('dbus:///org/pyneo/mapper')
			class_.timetable = object_by_url('dbus:///org/pyneo/Timetable')
			class_.http = object_by_url('dbus:///org/pyneo/NetHttp')
			class_.wlan = object_by_url('dbus:///org/pyneo/WlanDevice')
			class_.notify = object_by_url('dbus:///org/pyneo/Notify')
			class_.ggl = object_by_url('dbus:///org/pyneo/GoogleLocation')
			class_.news = object_by_url('dbus:///org/pyneo/News')
			class_.entry = object_by_url('dbus:///org/pyneo/Entry')

		except Exception, e:
			print "Pyneo error: " + str(e)
			if not class_._dbus_timer:
				class_._dbus_timer = ecore.timer_add(5, class_.init)

			# We had an error, keep the timer running if we were called by ecore
			return True

		# No error (anymore)
		if class_._dbus_timer: class_._dbus_timer.stop()

		# some theme settings
		class_.set_bg_image = class_.get_ini_value('theme', 'bg_image')
		class_.set_font_color = class_.get_ini_value('theme', 'font_color')
		class_.brightness_value = int(class_.get_ini_value('theme', 'brightness'))

		class_.call_type = None
		class_.call = None
		class_.gsm_net_status = {}
		class_.callsigs = []
		class_.alsastate = ['stereoout', 'gsmheadset', 'voipheadset', 'gsmspeakerout', 'gsmhandset']
		class_.alsacurrent = None
		class_.vibrate_state = ['on', 'off']
		class_.vibrate_current = None
		class_.syslog_state = ['on', 'off']
		if ConfigParser('/etc/pyneod.ini').get_section_config('sys').get('log_debug') == 'False':
			class_.syslog_current = 'off'
		else:
			class_.syslog_current = 'on'

		# Register our own D-Bus callbacks (device status, new calls, power status, new sms, new music title)
		class_.pwr.connect_to_signal('Status', class_.on_pwr_status, dbus_interface=DIN_POWERED)
		class_.music.connect_to_signal('Status', class_.on_music_status, dbus_interface=DIN_MUSIC)
		class_.music.connect_to_signal('Position', class_.on_music_position, dbus_interface=DIN_MUSIC)
		class_.map.connect_to_signal('NewFile', class_.on_map_new_file, dbus_interface=DIN_MAP)
		class_.gps.connect_to_signal('Position', class_.on_gps_position_status, dbus_interface=DIN_LOCATION)
		class_.gprs.connect_to_signal('Status', class_.on_gprs_status, dbus_interface=DIN_NETWORK)
		class_.news.connect_to_signal('New', class_.on_rss_news, dbus_interface=DIN_STORAGE)

		ecore.timer_add(1, class_.power_up_gsm)

	@classmethod
	def on_rss_news(class_, status):
		status = dedbusmap(status)
		print "News: " + str(status)
		for n in status:
			news = object_by_url(n)
			class_.notify_callbacks("show_news", dedbusmap(news.GetContent(dbus_interface=DIN_ENTRY, timeout=200)))

	@classmethod
	def get_pwr_status(class_):
		status = class_.pwr.GetStatus(dbus_interface=DIN_POWERED)
		class_.on_pwr_status(status)

	@classmethod
	def get_gprs_status(class_):
		status = class_.gprs.GetStatus(dbus_interface=DIN_NETWORK)
		class_.on_gprs_status(status)

	@classmethod
	def get_device_status(class_):
		class_.notify_callbacks("device_status", class_.gsm.GetStatus(dbus_interface=DIN_POWERED))

	@classmethod
	def power_status_gsm(class_):
		class_.notify_callbacks("power_status_gsm", class_.gsm.GetPower(APP_TITLE, dbus_interface=DIN_POWERED))

	@classmethod
	def get_hon(class_, reply_handler):
		def error(msg):
			print "error getting hon:", msg
		class_.hon.GetImage(dict(gender='w'), reply_handler=reply_handler, error_handler=error, dbus_interface=DIN_VOLATILE_IMAGE)

	@classmethod
	def vote_hon(class_, vote):
		class_.hon.GetImage(vote, dbus_interface=DIN_VOLATILE_IMAGE)

	@classmethod
	def show_sms_detail(class_, number, status):
		class_.notify_callbacks("show_sms_detail", number, status)

	@classmethod
	def power_up_gsm(class_):
		try:
			if class_.gsm.GetPower(APP_TITLE, dbus_interface=DIN_POWERED):
				print '---', 'gsm device is already on'
			else:
				class_.gsm.SetPower(APP_TITLE, True, dbus_interface=DIN_POWERED)
				print '---', 'switching gsm device on'
			class_.gsm_wireless = object_by_url(class_.gsm.GetDevice('wireless', dbus_interface=DIN_POWERED))
			class_.gsm_sms = object_by_url(class_.gsm.GetDevice('shortmessage_storage', dbus_interface=DIN_POWERED))
			class_.gsm_contacts = object_by_url(class_.gsm.GetDevice('phonebook_storage', dbus_interface=DIN_POWERED))

		except Exception, e:
			print "GSM error: " + str(e)
			if not class_._gsm_timer:
				class_._gsm_timer = ecore.timer_add(5, class_.power_up_gsm)

			# We had an error, keep the timer running if we were called by ecore
			return True

		# No error (anymore)
		if class_._gsm_timer: class_._gsm_timer.stop()

		class_.gsm_wireless.connect_to_signal('Status', class_.on_gsm_wireless_status, dbus_interface=DIN_WIRELESS)
		class_.gsm_wireless.connect_to_signal('New', class_.check_new_call, dbus_interface=DIN_WIRELESS)
		class_.gsm_sms.connect_to_signal('New', class_.check_new_sms, dbus_interface=DIN_STORAGE)

		class_.get_gsm_keyring()

	@classmethod
	def power_down_gsm(class_):
		class_.gsm.SetPower(APP_TITLE, False, dbus_interface=DIN_POWERED)
		class_.power_status_gsm()

	@classmethod
	def get_gsm_keyring(class_):
		try:
			class_.gsm_keyring = object_by_url(class_.gsm_wireless.GetKeyring(dbus_interface=DIN_AUTHORIZED))

		except Exception, e:
			print "SIM error: " + str(e)
			if not class_._keyring_timer:
				class_._keyring_timer = ecore.timer_add(5, class_.get_gsm_keyring)

			# We had an error, keep the timer running if we were called by ecore
			return True

		# No error (anymore)
		if class_._keyring_timer: class_._keyring_timer.stop()

		class_.gsm_keyring.connect_to_signal("Opened", class_.on_gsm_keyring_status, dbus_interface=DIN_KEYRING)

		# Inquire SIM status and act accordingly to the initial state
		status = class_.gsm_keyring.GetOpened(dbus_interface=DIN_KEYRING)
		class_.on_gsm_keyring_status(status)

	@classmethod
	def gsm_sim_locked(class_):
		return class_.gsm_keyring_status['code'] != 'READY'

	@classmethod
	def gsm_unlock_sim(class_, key):
		class_.gsm_keyring.Open(key, dbus_interface=DIN_KEYRING)

	@classmethod
	def gsm_dial(class_, number):
		class_.call_type = 'outgoing'
		if class_.alsacurrent == 'stereoout':
			class_.set_state_file('gsmhandset')
		elif class_.alsacurrent == 'voipheadset':
			class_.set_state_file('gsmheadset')
		try:
			name = class_.gsm_wireless.Initiate(number, dbus_interface=DIN_VOICE_CALL_INITIATOR, timeout=200)
			class_.call = object_by_url(name)
		except Exception, e:
			print "Dial error: " + str(e)
			class_.set_state_file(class_.alsacurrent)
			class_.notify_callbacks("gsm_phone_call_end")

	@classmethod
	def gsm_hangup(class_):
		class_.set_state_file(class_.alsacurrent)
		class_.dialer_text_set("")
		class_.call = object_by_url('dbus:///org/pyneo/gsmdevice/Call/1')
		class_.call.Hangup(dbus_interface=DIN_VOICE_CALL)

	@classmethod
	def gsm_accept(class_, number):
		class_.call_type = 'incoming'
		class_.sys.Vibrate(0, 0, 0, dbus_interface=DIN_SYSTEM)
		if class_.alsacurrent == 'stereoout':
			class_.set_state_file('gsmhandset')
		elif class_.alsacurrent == 'voipheadset':
			class_.set_state_file('gsmheadset')
		class_.call.Accept(dbus_interface=DIN_VOICE_CALL)

	@classmethod
	def gsm_details(class_):
		class_.notify_callbacks("gsm_details", class_.gsm_wireless.GetStatus(dbus_interface=DIN_WIRELESS))

	@classmethod
	def on_gsm_wireless_status(class_, status_map):
		status = dedbusmap(status_map)
		print 'GSM NET Status: %s'%status

		if 'stat' in status:
			nw_status = status['stat']

			if nw_status == 0:
				class_.notify_callbacks("gsm_unregistered")
			elif nw_status in (1, 5):
				class_.notify_callbacks("gsm_registered")
			elif nw_status == 2:
				class_.notify_callbacks("gsm_registering")
			elif nw_status == 3:
				class_.notify_callbacks("gsm_reg_denied")
			elif nw_status == 4:
				raise NotImplementedError("GSM registration has unknown state")

		for text in ['rssi', 'oper', 'lac', 'ci', 'mcc']:
			if text in status:
				class_.gsm_net_status[text] = status[text]
				if text == 'rssi':
					class_.notify_callbacks("gsm_signal_strength_change", status['rssi'])
				if text == 'oper':
					class_.notify_callbacks("gsm_operator_change", status['oper'])
				if text == 'mcc':
					results = DatabaseController.get_country_code(str(status['mcc']))
					class_.gsm_net_status['cc'] = results[0][1]
					class_.gsm_net_status['country'] = results[0][0]
		class_.notify_callbacks("gsm_details", class_.gsm_net_status)

	@classmethod
	def on_gsm_keyring_status(class_, status_map):
		status = dedbusmap(status_map)
		class_.gsm_keyring_status = status
		print "SIM Status: " + str(status)

		if status["code"] == "READY":
			class_.notify_callbacks("sim_ready")

			# Try registering on the network
			res = dedbusmap(class_.gsm_wireless.GetStatus(dbus_interface=DIN_WIRELESS, ))
			if not res['stat'] in (1, 5, ):
				print '---', 'registering to gsm network'
				class_.gsm_wireless.Register(dbus_interface=DIN_WIRELESS, timeout=200)
				res = dedbusmap(class_.gsm_wireless.GetStatus(dbus_interface=DIN_WIRELESS, ))
			else:
				print '---', 'already registered'
		else:
			class_.notify_callbacks("sim_key_required", status["code"])

	@classmethod
	def activate_gprs(class_):
		status = class_.gprs.Activate(True, dbus_interface=DIN_NETWORK)
		class_.on_gprs_status(status)

	@classmethod
	def deactivate_gprs(class_):
		status = class_.gprs.Activate(False, dbus_interface=DIN_NETWORK)
		class_.on_gprs_status(status)

	@classmethod
	def power_status_gps(class_):
		class_.notify_callbacks("power_status_gps", class_.gps.GetPower(APP_TITLE, dbus_interface=DIN_POWERED))

	@classmethod
	def power_up_gps(class_):
		print 'power_up_gps'
		try:
			if class_.gps.GetPower(APP_TITLE, dbus_interface=DIN_POWERED):
				print '---', 'gps device is already on'
			else:
				class_.gps.SetPower(APP_TITLE, True, dbus_interface=DIN_POWERED)
				print '---', 'switching gps device on'

		except Exception, e:
			print "GPS error: " + str(e)
			if not class_._gps_timer:
				class_._gps_timer = ecore.timer_add(5, class_.power_up_gps)

			# We had an error, keep the timer running if we were called by ecore
			return True

		# No error (anymore)
		if class_._gps_timer: class_._gps_timer.stop()

		class_.notify_callbacks("power_status_gps", class_.gps.GetPower(APP_TITLE, dbus_interface=DIN_POWERED))

		status = class_.gps.GetPosition(dbus_interface=DIN_LOCATION)
		class_.on_gps_position_status(status)

	@classmethod
	def power_down_gps(class_):
		class_.gps.SetPower(APP_TITLE, False, dbus_interface=DIN_POWERED)
		class_.notify_callbacks("power_status_gps", class_.gps.GetPower(APP_TITLE, dbus_interface=DIN_POWERED))

	@classmethod
	def on_gps_position_status(class_, status):
		status = dedbusmap(status)
		print "GPS Status: " + str(status)
		class_.notify_callbacks("gps_position_change", status)

	@classmethod
	def on_gprs_status(class_, status):
		status = dedbusmap(status)
		print "GPRS Status: " + str(status)
		class_.notify_callbacks("gprs_status", status)

	@classmethod
	def on_map_new_file(class_, newmap):
		newmap = dedbusmap(newmap)
		class_.notify_callbacks("on_map_new_file", newmap)

	@classmethod
	def map_request_tiles(class_, latitude, longitude, zoom, map_type):
		class_.map_tiles.get(map_type, "OsmStreet").RequestMap(dict(latitude=latitude,longitude=longitude,zoom=zoom,delta_x=480,delta_y=640), dbus_interface=DIN_MAP)

	@classmethod
	def on_pwr_status(class_, status_map):
		status = dedbusmap(status_map)
		print "POWER Status: " + str(status)
		class_.notify_callbacks("capacity_change", status)
		class_.notify_callbacks("pwr_status_change", status)

	@classmethod
	def show_dialer_screen(class_):
		class_.pwr.GetStatus(dbus_interface=DIN_POWERED)
		class_.notify_callbacks("show_dialer_screen")

	@classmethod
	def show_gsm_status_screen(class_):
		class_.notify_callbacks("show_gsm_status_screen")

	@classmethod
	def show_gps_status_screen(class_):
		class_.notify_callbacks("show_gps_status_screen")

	@classmethod
	def show_gps_map_screen(class_):
		class_.notify_callbacks("show_gps_map_screen")

	@classmethod
	def show_incall_screen(class_, calling_type):
		class_.call_type = calling_type
		print "CALLING_TYPE: ", class_.call_type
		class_.notify_callbacks("gsm_phone_call_start")

	@classmethod
	def show_lock_screen(class_):
		class_.notify_callbacks("show_lock_screen")

	@classmethod
	def brightness_change(class_, status):
		class_.brightness_value += status
		if class_.brightness_value > 100: class_.brightness_value = 100
		if class_.brightness_value < 0: class_.brightness_value = 0
		class_.sys.SetBrightness(class_.brightness_value, dbus_interface=DIN_SYSTEM)
		class_.notify_callbacks("brightness_change", class_.brightness_value)

	@classmethod
	def scan_operator(class_, reply_handler, error_handler):
		class_.gsm_wireless.Scan(timeout=100.0, reply_handler=reply_handler, error_handler=error_handler, dbus_interface=DIN_WIRELESS, )

	@classmethod
	def scan_wireless(class_):
		class_.notify_callbacks("scan_wireless", dedbusmap(class_.wlan.Scan(timeout=100.0, dbus_interface=DIN_WIRELESS, )))

	@classmethod
	def check_new_call(class_, newmap):
		def CallStatus(newmap):
			newmap = dedbusmap(newmap)
			class_.notify_callbacks("gsm_phone_ringing")
			if newmap['number']:
				class_.notify_callbacks("gsm_number_display", newmap['number'])
			else:
				class_.notify_callbacks("gsm_number_display", 'restricted')
			print '---', 'CallStatus'

		def CallRing(newmap):
			newmap = dedbusmap(newmap)
			class_.notify_callbacks("gsm_phone_ringing")
			if newmap['number']:
				class_.notify_callbacks("gsm_number_display", newmap['number'])
			else:
				class_.notify_callbacks("gsm_number_display", 'restricted')
			print '---', 'CallRing', newmap

		def CallEnd(newmap):
			class_.notify.StopTone('ring')
			class_.sys.Vibrate(0, 0, 0, dbus_interface=DIN_SYSTEM)
			class_.notify_callbacks("gsm_phone_call_end")
			class_.set_state_file('stereoout')
			newmap = dedbusmap(newmap)
			print '---', 'CallEnd'
			if class_.call:
				class_.call = None
				while class_.callsigs:
					class_.callsigs.pop().remove()

			DatabaseController.insert_history(class_.call_type, newmap['number'])
			if class_.call_type == 'missed':
				PyneoController.set_missed_call_icon('true')
				cp = ConfigParser(INI_PATH)
				cp.get_section_config('status').set('missed_calls', 'true')
				cp.save()
			class_.dialer_text_set("")
			class_.call_type = None
			class_.gsm_wireless.GetStatus(dbus_interface=DIN_WIRELESS)

		newmap = dedbusmap(newmap)
		print '---', 'CallNew: ', class_.call_type
		if not class_.call_type:
			class_.notify.PlayTone('ring')
			if PyneoController.vibrate_current == 'on':
				class_.sys.Vibrate(800, 200, 0, dbus_interface=DIN_SYSTEM)
		if class_.call_type == 'outgoing' or class_.call_type == 'incoming':
			pass
		else:
			class_.call_type = 'missed'
		for n, v in newmap.items():
			class_.call = object_by_url(n)
			class_.callsigs.append(class_.call.connect_to_signal('Ring', CallRing, dbus_interface=DIN_VOICE_CALL, ))
			class_.callsigs.append(class_.call.connect_to_signal('Status', CallStatus, dbus_interface=DIN_VOICE_CALL, ))
			class_.callsigs.append(class_.call.connect_to_signal('End', CallEnd, dbus_interface=DIN_VOICE_CALL, ))

	@classmethod
	def set_missed_call_icon(class_, status):
		print "Set Missed Call Icon: ", status
		class_.notify_callbacks("set_missed_call_icon", status)

	@classmethod
	def on_music_status(class_, newmap):
		newmap = dedbusmap(newmap)
		print 'Music Status: %s' %newmap
		class_.notify_callbacks("on_get_music_tags", newmap)

	@classmethod
	def on_music_position(class_, position, duration):
		print 'Music Position: %d:%d'%(position, duration)
		class_.notify_callbacks("on_get_music_position", position, duration)

	@classmethod
	def check_new_sms(class_, newmap):
		class_.notify.PlayTone('sms')
		res = dedbusmap(newmap)
		for n in res:
			sm = object_by_url(n)
			content = dedbusmap(sm.GetContent(dbus_interface=DIN_ENTRY, timeout=200))
			DatabaseController.insert_new_sms('REC UNREAD', content['from_msisdn'], content['text'].encode('utf-8'), content['time'])
			print '--- NEW SMS:', content['from_msisdn'], content['time'], content['text'].encode('utf-8')
#		class_.gsm_sms.DeleteAll(dbus_interface=DIN_STORAGE, timeout=200)

	@classmethod
	def first_check_new_sms(class_):
		try:
			res = class_.gsm_sms.ListAll(dbus_interface=DIN_STORAGE)
			for n in res:
				sm = object_by_url(n)
				content = dedbusmap(sm.GetContent(dbus_interface=DIN_ENTRY))
				DatabaseController.insert_new_sms('REC UNREAD', content['from_msisdn'], content['text'].encode('utf-8'), content['time'])
		except:
			print '--- NULL new sms'
#		class_.gsm_sms.DeleteAll(dbus_interface=DIN_STORAGE)

	@ classmethod
	def get_phbook_raw(class_, reply_handler, error_handler):
		''' Get the raw output of the phonebook_storage '''
		print '-----', 'get the raw phonebook storage output'
		class_.gsm_contacts.ListAll(reply_handler=reply_handler, error_handler=error_handler, dbus_interface=DIN_STORAGE) # list all contacts and phonebooks

	@classmethod
	def get_phbook(class_, phbook_raw):
		""" Get the simcontacts as dict{name:number} """

		print '-----', 'get phonebookstorage, sim contacts'
		contactssim = {} # create a empty dictionary
		for n in phbook_raw:
			pbe = object_by_url(n)
			content = dedbusmap(pbe.GetContent())
			if content['phonebook'] == "SM": # SM is the phonebook with the sim contacts
				contactssim[content['text'].encode('utf-8')]  = content['number'] # name and number from => contactssim dict
		return contactssim

	@classmethod
	def show_screen(class_, screen):
		print '--- show ', screen
		class_.notify_callbacks("show_screen", screen)

	@classmethod
	def vibrate_start(class_):
		class_.sys.Vibrate(10, 3, 1, dbus_interface=DIN_SYSTEM)

	@classmethod
	def vibrate_stop(class_):
		class_.sys.Vibrate(0, 0, 0, dbus_interface=DIN_SYSTEM)

	@classmethod
	def show_audio_screen(class_):
		class_.notify_callbacks("show_audio_screen")

	@classmethod
	def play_music(class_):
		class_.music.Play(dbus_interface=DIN_MUSIC)

	@classmethod
	def stop_music(class_):
		class_.music.Stop(dbus_interface=DIN_MUSIC)

	@classmethod
	def pause_music(class_):
		class_.music.Pause(dbus_interface=DIN_MUSIC)

	@classmethod
	def next_music(class_):
		class_.music.Next(dbus_interface=DIN_MUSIC)
	@classmethod
	def previous_music(class_):
		class_.music.Previous(dbus_interface=DIN_MUSIC)

	@classmethod
	def set_playlist_from_dir(class_, path):
		class_.music.SetPlaylistFromDir(path, 'true', dbus_interface=DIN_MUSIC)

	@classmethod
	def get_music_tags(class_):
		class_.notify_callbacks("on_get_music_tags", class_.music.GetStatus(dbus_interface=DIN_MUSIC))

	@classmethod
	def set_volume(class_, status):
		class_.music.SetVolume(status, dbus_interface=DIN_MUSIC)

	@classmethod
	def set_tone(class_, themename, tone, sound_file):
		class_.notify.SetTone(themename, tone, sound_file, dbus_interface=DIN_NOTIFY)

	@classmethod
	def set_tone_volume(class_, themename, tone, status):
		class_.notify.SetToneVolume(themename, tone, status, dbus_interface=DIN_NOTIFY)

	@classmethod
	def play_tone(class_, tone):
		class_.notify.PlayTone(tone, dbus_interface=DIN_NOTIFY)

	@classmethod
	def stop_tone(class_, tone):
		class_.notify.StopTone(tone, dbus_interface=DIN_NOTIFY)

	@classmethod
	def create_theme(class_, themename):
		class_.notify.CreateTheme(themename, dbus_interface=DIN_NOTIFY)

	@classmethod
	def delete_theme(class_, themename):
		class_.notify.DeleteTheme(themename, dbus_interface=DIN_NOTIFY)

	@classmethod
	def set_current_theme(class_, themename):
		class_.notify.SetCurrentTheme(themename, dbus_interface=DIN_NOTIFY)

	@classmethod
	def set_tone_times(class_, themename, tone, times):
		class_.notify.SetToneTimes(themename, tone, times, dbus_interface=DIN_NOTIFY)

	@classmethod
	def get_song_duration(class_):
		class_.notify_callbacks('on_get_song_duration', class_.music.GetSongDuration(dbus_interface=DIN_MUSIC))

	@classmethod
	def get_song_position(class_):
		class_.notify_callbacks('on_get_song_position', class_.music.GetSongPosition(dbus_interface=DIN_MUSIC))

	@classmethod
	def set_state_file(class_, status):
		assert status in class_.alsastate
		print '--- Set ALSA state to', status
		class_.sys.SetAudioState(status, dbus_interface=DIN_SYSTEM)
		class_.alsacurrent = status

	@classmethod
	def sort_playlist(class_, order, key):
		class_.music.SortPlaylist(order, key, dbus_interface=DIN_MUSIC)
		print '--- Sort Playlist', order, key

	@classmethod
	def get_playlist(class_):
		class_.notify_callbacks('on_get_playlist', class_.music.GetPlaylist(dbus_interface=DIN_MUSIC))

	@classmethod
	def get_amazon_cover(class_, searchwords, file_name, reply_handler, error_handler):
		class_.ama.SearchCover(searchwords, file_name, reply_handler=reply_handler, error_handler=error_handler, dbus_interface='org.pyneo.AlbumCoverLookup')

	@classmethod
	def get_track(class_, start, destination, reply_handler, error_handler):
		class_.timetable.GetTracks(dict(start=start, destination=destination), reply_handler=reply_handler, error_handler=error_handler, dbus_interface='org.pyneo.Timetable')

	@classmethod
	def db_check(class_):
		if not isfile(DB_FILE_PATH):
			DatabaseInit.init()
			print '--- Add sqlite db'

	@classmethod
	def path_check(class_, path):
		if not exists(path):
			mkdir(path)
			print '--- Add missing directory'

	@classmethod
	def dialer_text_set(class_, text):
		class_.notify_callbacks('dialer_text_set', text)

	@classmethod
	def urlread(class_, url, reply_handler):
		filename = "/tmp/"+url
		def readurl(newmap):
			content = open(filename).read()
			unlink(filename)
			reply_handler(content)
		def error(msg):
			print "error getting url %s: %s" % (url, msg)
		class_.http.Request({
			'url':url,
			'cachefilename':filename,
			}, reply_handler=readurl, error_handler=error, dbus_interface=DIN_NETPROTOCOLS)

	@classmethod
	def set_track_record(class_, track_file):
		class_.gps.SetRecord(track_file, dbus_interface=DIN_LOCATION)

	@classmethod
	def set_debug_log(class_, status):
		if status == 'off':
			class_.sys.SetDebugLog(False, dbus_interface=DIN_SYSTEM)
		else:
			class_.sys.SetDebugLog(True, dbus_interface=DIN_SYSTEM)
		class_.notify_callbacks('set_syslog_txt', status)

	@classmethod
	def reload_font_color(class_):
		class_.set_font_color = class_.get_ini_value('theme', 'font_color')

	@classmethod
	def get_geocoding(class_, lat, lon):
		class_.notify_callbacks('on_get_geocoding', class_.ggl.GeoCoding(lat, lon, dbus_interface=DIN_LOCATION))

	@classmethod
	def powered_news(class_, status):
		class_.news.SetPower(APP_TITLE, status, dbus_interface=DIN_POWERED)
		print '--- SetPower News Daemon', status

	@classmethod
	def set_missed_medium_icon(class_, status, medium):
		class_.notify_callbacks("set_missed_medium_icon", status, medium)
		print '--- SetMissedMediumIcon', status, medium

	@classmethod
	def get_ini_value(class_, section, control):
		cp = ConfigParser(INI_PATH)
		return cp.get_section_config(section).get(control)

	@classmethod
	def set_ini_value(class_, section, control, value):
		cp = ConfigParser(INI_PATH)
		cp.get_section_config(section).set(control, value)
		cp.save()

from dialer_screen import *
from incall_screen import *
from gsm_status_screen import *
from gps_status_screen import *
from gps_map_screen import *
#from time_screen import *
from hon_screen import *
from lock_screen import *
from pix_screen import *
from contacts_screen import *
from sms_screen import *
from sms_detail import *
from weather_screen import *
from audio_screen import *
from history_screen import *
from settings_screen import *
from timetable_screen import *
from simimporter_screen import *
from wlan_screen import *
from fontcolor_screen import *
from audiosort_screen import *
from news_screen import *

class Dialer(object):
	screens = None
	evas_canvas = None
	system_bus = None

	def __init__(self):
		# Initialize the GUI
#		edje.frametime_set(FRAMETIME)
		self.evas_canvas = EvasCanvas(FULLSCREEN)

		self.screens = {}

		# Register our own callbacks
		PyneoController.register_callback("gsm_phone_ringing", self.on_ringing)
		PyneoController.register_callback("gsm_phone_call_start", self.on_call_start)
		PyneoController.register_callback("gsm_phone_call_end", self.on_call_end)
		PyneoController.register_callback("show_gps_status_screen", self.on_gps_status_screen)
		PyneoController.register_callback("show_gps_map_screen", self.on_gps_map_screen)
		PyneoController.register_callback("show_dialer_screen", self.on_call_end)
		PyneoController.register_callback("show_lock_screen", self.on_lock_screen)
		PyneoController.register_callback("show_audio_screen", self.on_audio_screen)
		PyneoController.register_callback("show_screen", self.on_show_screen)

		# Initialize the D-Bus interface to pyneo
		dbus_ml = DBusEcoreMainLoop()
		self.system_bus = SystemBus(mainloop=dbus_ml)
		PyneoController.init()
		PyneoController.path_check(DB_PATH)
		PyneoController.db_check()
		DatabaseController.init()

		self.init_screen(DIALER_SCREEN_NAME, DialerScreen)
		PyneoController.show_dialer_screen()
		PyneoController.brightness_change(0)

		ecore.timer_add(1, self.load_screens)

	def load_screens(self):
		self.init_screen(INCALL_SCREEN_NAME, InCallScreen)
		self.init_screen(GPS_STATUS_SCREEN_NAME, GpsStatusScreen)
		self.init_screen(GPS_MAP_SCREEN_NAME, GpsMapScreen)
		self.init_screen(AUDIO_SCREEN_NAME, AudioScreen)

		PyneoController.power_status_gps()

		try:
			PyneoController.create_theme('blackwhite')
			PyneoController.set_tone('blackwhite', 'ring', PyneoController.get_ini_value('theme', 'ringtone_file'))
			PyneoController.set_tone('blackwhite', 'sms', PyneoController.get_ini_value('theme', 'smstone_file'))
			PyneoController.set_tone_volume('blackwhite', 'ring', 0.3)
			PyneoController.set_tone_volume('blackwhite', 'sms', 0.9)
			PyneoController.set_tone_times('blackwhite', 'sms', 3)
			PyneoController.set_current_theme('blackwhite')
			PyneoController.set_state_file(PyneoController.get_ini_value('alsa', 'alsastate'))
			PyneoController.vibrate_current = PyneoController.get_ini_value('theme', 'vibrate')
			PyneoController.set_missed_medium_icon(PyneoController.get_ini_value('status', 'missed_calls'), 'calls')
			PyneoController.set_missed_medium_icon(PyneoController.get_ini_value('status', 'missed_sms'), 'sms')
		except Exception, error:
			print "ERROR: unable to load theme things: %s" % error

		self.init_screen(LOCK_SCREEN_NAME, LockScreen)
		PyneoController.power_status_gsm()

	def init_screen(self, screen_name, constructor):
		if screen_name in self.screens.keys():
			return

		try:
			instance = constructor(self)
			self.screens[screen_name] = instance
			self.evas_canvas.evas_obj.data[screen_name] = instance

			# register the screen default callbacks
			instance.register_pyneo_callbacks()
		except Exception, error:
			print "ERROR: screen %s failed to load, reason: %s" % (screen_name, error)

	def show_screen(self, screen_name):
		if screen_name not in self.screens.keys():
			print "screen %s not available"%screen_name
		else:
			for (name, screen) in self.screens.items():
				if name == screen_name:
					screen.show()
				else:
					screen.hide()

	def get_evas(self):
		return self.evas_canvas.evas_obj.evas

	def on_ringing(self):
		self.show_screen(INCALL_SCREEN_NAME)

	def on_call_start(self):
		self.show_screen(INCALL_SCREEN_NAME)

	def on_call_end(self):
		self.show_screen(DIALER_SCREEN_NAME)

	def on_gps_status_screen(self):
		self.show_screen(GPS_STATUS_SCREEN_NAME)

	def on_gps_map_screen(self):
		self.show_screen(GPS_MAP_SCREEN_NAME)

	def on_lock_screen(self):
		self.show_screen(LOCK_SCREEN_NAME)

	def on_sms_screen_detail(self):
		self.show_screen(SMS_DETAIL_SCREEN_NAME)

	def on_audio_screen(self):
		self.show_screen(AUDIO_SCREEN_NAME)

	def on_show_screen(self, screen):
		if screen == WEATHER_SCREEN_NAME:
			self.init_screen(screen, WeatherScreen)
		elif screen == WLAN_SCREEN_NAME:
			self.init_screen(screen, WlanScreen)
		elif screen == TIMETABLE_SCREEN_NAME:
			self.init_screen(screen, TimetableScreen)
		elif screen == SIMIMPORTER_SCREEN_NAME:
			self.init_screen(screen, SimImporter)
		elif screen == SETTINGS_SCREEN_NAME:
			self.init_screen(screen, SettingsScreen)
		elif screen == HON_SCREEN_NAME:
			self.init_screen(screen, HonScreen)
		elif screen == PIX_SCREEN_NAME:
			self.init_screen(screen, PixScreen)
		elif screen == TIME_SCREEN_NAME:
			self.init_screen(screen, TimeScreen)
		elif screen == SMS_SCREEN_NAME:
			self.init_screen(screen, SmsScreen)
		elif screen == FONTCOLOR_SCREEN_NAME:
			self.init_screen(screen, FontcolorScreen)
		elif screen == AUDIOSORT_SCREEN_NAME:
			self.init_screen(screen, AudiosortScreen)
		elif screen == NEWS_SCREEN_NAME:
			self.init_screen(screen, NewsScreen)
		elif screen == GSM_STATUS_SCREEN_NAME:
			self.init_screen(screen, GsmStatusScreen)
		elif screen == HISTORY_SCREEN_NAME:
			self.init_screen(screen, HistoryScreen)
		elif screen == CONTACTS_SCREEN_NAME:
			self.init_screen(screen, ContactsScreen)
		elif screen == SMS_DETAIL_SCREEN_NAME:
			self.init_screen(screen, SmsDetail)
		self.show_screen(screen)

class EvasCanvas(object):
	def __init__(self, fullscreen, engine_name="x11"):
		if engine_name == "x11":
			engine = ecore.evas.SoftwareX11
		elif engine_name == "x11":
			print "warning: x11-16 is not supported, falling back to x11"
			engine = ecore.evas.SoftwareX11
		else:
			raise Exception("unknwon engine %s"% engine_name)

		self.evas_obj = engine(w=WIDTH, h=HEIGHT)
		if not self.evas_obj.evas:
			raise Exception("e did not init")
		self.evas_obj.callback_delete_request = self.on_delete_request
		self.evas_obj.callback_resize = self.on_resize

		self.evas_obj.title = APP_TITLE
		self.evas_obj.name_class = WM_INFO
		self.evas_obj.fullscreen = fullscreen
#		self.evas_obj.size = str(WIDTH) + 'x' + str(HEIGHT)
		self.evas_obj.evas.image_cache_set(IMAGE_CACHE_SIZE*1024*1024)
		self.evas_obj.evas.font_cache_set(FONT_CACHE_SIZE*1024*1024)
		self.evas_obj.show()

	def on_resize(self, evas_obj):
		x, y, w, h = evas_obj.evas.viewport
		size = (w, h)
		for key in evas_obj.data.keys():
			evas_obj.data[key].size = size

	def on_delete_request(self, evas_obj):
		ecore.main_loop_quit()


if __name__ == "__main__":
	Dialer()
	ecore.main_loop_begin()

'''
export LDFLAGS="$LDFLAGS -L/opt/e17/lib"
export PKG_CONFIG_PATH="/opt/e17/lib/pkgconfig:$PKG_CONFIG_PATH"
export PATH="$PATH:/opt/e17/bin"
export PYTHONPATH="/home/fgau/usr/lib/python2.5/site-packages"
'''


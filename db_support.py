#!/usr/bin/env python2.5
# -*- coding: utf-8 -*-
__author__ = "Frank Gau (fgau@pyneo.org), Thomas Gstaedtner (thomas (a) gstaedtner (.) net), Johannes 'josch' Schauer <j.schauer@email.de>"
__version__ = "prototype"
__copyright__ = "Copyright (c) 2009"
__license__ = "GPL3"

from datetime import datetime
from sqlite3 import connect
from constants import DB_FILE_PATH

class DatabaseController(object):
	@classmethod
	def init(class_):
		class_.connection = connect(DB_FILE_PATH)
		class_.cursor = class_.connection.cursor()

	@classmethod
	def get_sms_count(class_, status):
		class_.cursor.execute("SELECT COUNT(*) FROM sms WHERE status='%s'" % status)
		results = [i for i in class_.cursor]
		if len(results) == 1:
			return results[0][0]

	@classmethod
	def get_call_count(class_, status):
		if status == 'time':
			class_.cursor.execute("SELECT COUNT(*) FROM calls")
		else:
			class_.cursor.execute("SELECT COUNT(*) FROM calls WHERE status='%s'" % status)
		results = [i for i in class_.cursor]
		if len(results) == 1:
			return results[0][0]

	@classmethod
	def get_contact_count(class_):
		class_.cursor.execute("SELECT COUNT(*) FROM contacts")
		results = [i for i in class_.cursor]
		if len(results) == 1:
			return results[0][0]

	@classmethod
	def get_name_from_number(class_, number):
		class_.cursor.execute("SELECT name FROM contacts WHERE number LIKE ? LIMIT 1", ("%%%s"%number,))
		results = [i for i in class_.cursor]
		if len(results) == 1:
			return results[0][0]

	@classmethod
	def get_number_from_name(class_, name):
		class_.cursor.execute("SELECT number FROM contacts WHERE name LIKE ? LIMIT 1", ("%%%s%%"%name,))
		results = [i for i in class_.cursor]
		if len(results) == 1:
			return results[0][0]

	@classmethod
	def get_contacts(class_, count, offset):
		class_.cursor.execute("SELECT * FROM contacts ORDER BY 'name' LIMIT ? OFFSET ?", (count, offset))
		return class_.cursor

	@classmethod
	def get_sms_list(class_, count, offset, status):
		class_.cursor.execute("SELECT * FROM sms WHERE status='%s' ORDER BY time DESC LIMIT %s OFFSET %s" %(status, count, offset))
		results = [i for i in class_.cursor]
		if len(results):
			return results

	@classmethod
	def get_allcontacts(class_):
		class_.cursor.execute("SELECT name, number FROM contacts")
		contactsdb = {}
		for name, number in class_.cursor:
			contactsdb[name.encode("utf-8")] = number
		return contactsdb

	@classmethod
	def insert_history(class_, status, number):
		class_.cursor.execute('INSERT INTO calls (status, number, time) VALUES (?, ?, ?)', (status, number, datetime.now()))
		class_.connection.commit()

	@classmethod
	def insert_contact(class_, number, name):
		class_.cursor.execute('INSERT INTO contacts (name, number) VALUES (?, ?)', (name, number))
		class_.connection.commit()

	@classmethod
	def insert_new_sms(class_, status, number, text, time):
		class_.cursor.execute('INSERT INTO sms (status, number, text, time) VALUES (?, ?, ?, ?)', (status, number, text, time))
		class_.connection.commit()

	@classmethod
	def del_allcontacts(class_):
		class_.cursor.execute("DELETE FROM contacts")
		class_.connection.commit()

	@classmethod
	def get_country_code(class_, mcc):
		class_.cursor.execute("SELECT * FROM mcc WHERE mcc='%s'" % mcc)
		results = [i for i in class_.cursor]
		if len(results) == 1:
			return results

	@classmethod
	def mark_sms_read(class_, time):
		class_.cursor.execute("UPDATE sms SET status='REC READ' WHERE time='%s'" % time)
		class_.connection.commit()

	@classmethod
	def get_sms_detail(class_, sms_number, sms_status):
		class_.cursor.execute("SELECT * FROM sms WHERE status='%s' ORDER BY time DESC LIMIT 1 OFFSET %s" %(sms_status, sms_number))
		results = [i for i in class_.cursor]
		if len(results) == 1:
			return results

	@classmethod
	def check_for_unread_sms(class_):
		class_.cursor.execute("SELECT COUNT(*) FROM sms WHERE status='REC UNREAD'")
		for row in class_.cursor:
			print 'Count: ', row[0]
		return row[0]

	@classmethod
	def delete_sms(class_, time):
		class_.cursor.execute("DELETE FROM sms WHERE time='%s'" % time)
		class_.connection.commit()

	@classmethod
	def get_calls(class_, status, limit, offset):
		class_.cursor.execute("SELECT * FROM calls WHERE status LIKE ? ORDER by time DESC LIMIT ? OFFSET ?", (status, limit, offset))
		results = [i for i in class_.cursor]
		if len(results):
			return results

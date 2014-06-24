#!/usr/bin/env python2.5
# -*- coding: utf-8 -*-
__author__ = "Johannes 'josch' Schauer <j.schauer@email.de>"
__version__ = "prototype"
__copyright__ = "Copyright (c) 2009 J. Schauer"
__license__ = "GPL3"

from epydial import *

class Station(object):
    def __init__(self, canvas, num, station, arrival=None, arrival_track=None, departure=None, departure_track=None, train_type=None, train_id=None):
        self.rect = evas.Rectangle(canvas, pos=(480/20, (640*2)/11+num*640/7), size=((480*18)/20, 640/9), color="#38ffffff")
        self.rect.layer = 2

        if arrival:
            arrival = datetime.strptime(arrival, "%Y-%m-%dT%H:%M:%S").strftime("%H:%M")
            label1_text = ("%s %s Gl. %s"%(station, arrival, arrival_track)).encode("utf8")
        else:
            label1_text = station
        self.label1 = evas.Text(canvas, text=label1_text, font=("Sans,Edje-Vera", 26), color="#80ffffff")
        self.label1.layer = 3
        self.label1.pass_events = True
        self.label1.pos = (480/20+4, (640*2)/11+num*640/7+2)

        if departure:
            departure = datetime.strptime(departure, "%Y-%m-%dT%H:%M:%S").strftime("%H:%M")
            label2_text = "%s Gl. %s - %s %s"%(departure, departure_track, train_type, train_id)
        else:
            label2_text = ""
        self.label2 = evas.Text(canvas, text=label2_text, font=("Sans,Edje-Vera", 26), color="#80ffffff")
        self.label2.layer = 3
        self.label2.pass_events = True
        self.label2.pos = (480/20+4, (640*2)/11+num*640/7+34)

    def show(self):
        self.rect.show()
        self.label1.show()
        self.label2.show()

    def hide(self):
        self.rect.hide()
        self.label1.hide()
        self.label2.hide()

class TimetableScreen(object):
    def register_pyneo_callbacks(self):
        pass

    def __init__(self, screen_manager):
        self.buttons = {}
        self.visible = False
        self.canvas = screen_manager.get_evas()

        self.bg = evas.Image(self.canvas, pos=(0, 0), size=(WIDTH, HEIGHT), file=PyneoController.set_bg_image)
        self.bg.fill = 0, 0, WIDTH, HEIGHT
        self.bg.layer = 0

        self.headline = evas.Text(self.canvas, font=("Sans,Edje-Vera", 40), color="#808080")
        self.headline.layer = 1

        self.subheadline = evas.Text(self.canvas, font=("Sans:style=Bold,Edje-Vera", 30), color="#808080")
        self.subheadline.layer = 1

        for pos, text, action in ((0, "back", lambda source, event: PyneoController.show_dialer_screen()),
                                  (2, "previous", lambda source, event: None),
                                  (3, "next", lambda source, event: None)):
            self.buttons[text] = self.init_button(text, (pos+1)*16+pos*100, 524, 100, 100, action)

        self.stations = list()
        self.get_tracks()

    def init_button(self, name, x, y, dx, dy, action):
        button = evas.Image(self.canvas, pos=(x,y), size=(dx,dy), file="/usr/share/epydial/data/themes_data/blackwhite/images/%s.png" % name)
        button.fill = 0, 0, dx, dy
        button.layer = 99
        button.on_mouse_up_add(action)
        return button

    def get_tracks(self):
        def ok_cb(newmap):
            newmap =dedbusmap(newmap)
            arrival = datetime.strptime(newmap['arrival'], "%Y-%m-%dT%H:%M:%S").strftime("%H:%M")
            departure = datetime.strptime(newmap['departure'], "%Y-%m-%dT%H:%M:%S").strftime("%H:%M")
            self.subheadline.text = "%s - %s (%s EUR)"%(departure, arrival, round(newmap.get('cost', 0)/100.0, 2))
            self.subheadline.pos = ((480-self.subheadline.horiz_advance)/2, 70)
            for num, s in enumerate(newmap['stations']):
                self.stations.append(Station(self.canvas, num, **s))
            if self.visible:
                for station in self.stations:
                    station.show()
        def error_cb(msg):
            print "error:", msg
        self.headline.text = "Karlsruhe - Düsseldorf"
        self.headline.pos = ((480-self.headline.horiz_advance)/2, 12)
        PyneoController.get_track("Karlsruhe", "Düsseldorf", ok_cb, error_cb)


    def show(self):
        self.visible = True
        self.bg.show()
        self.headline.show()
        self.subheadline.show()
        for station in self.stations:
            station.show()
        for button in self.buttons.values():
            button.show()

    def hide(self):
        self.visible = False
        self.bg.hide()
        self.headline.hide()
        self.subheadline.hide()
        for station in self.stations:
            station.hide()
        for button in self.buttons.values():
            button.hide()

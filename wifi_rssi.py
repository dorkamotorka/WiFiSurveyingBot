#!/usr/bin/env python2
# -*- encoding: utf-8 -*-

import dbus
import os
import sys
from gi.repository import GObject as gobject
from gi.repository import GLib as glib
from dbus.mainloop.glib import DBusGMainLoop
import logging as log
import argparse
import time
import paho.mqtt.client as mqtt
try:
    import matplotlib.pyplot as plt
except ImportError:
    pass

def is_python_3():
    return sys.version_info[0] >= 3

def is_python_2():
    return not(is_python_3())

# The callback for when a PUBLISH message is received from the server.
def on_message(client, userdata, msg):
    print("Topic: {} / Message: {}".format(msg.topic,str(msg.payload.decode("UTF-8"))))
    if(msg.payload.decode("UTF-8") == "Reply"):
        client.publish("python", os.environ.get('OS',''))

class WiFiList():
    def __init__(self, watched):
        self.bus = dbus.SystemBus()
        self.NM = 'org.freedesktop.NetworkManager'
        self.bus.add_signal_receiver(
            self.handle_rssi_change, None, self.NM + '.AccessPoint', None, None)
        nm = self.bus.get_object(self.NM, '/org/freedesktop/NetworkManager')
        self.devlist = nm.GetDevices(dbus_interface=self.NM)
        self.rssid = {}
        self.data = {}
        self.watched = watched
        if is_python_2():
            self.watched = [i.decode('utf-8') for i in watched]
        self.start_time = time.time()
        self.xaxis = []

    def __repr__(self):
        return "\n".join(["%35s: %5d" % (k, j) for k, j in self.rssid.items()])

    def get_wifi_dict(self):
	return self.rssid

    def dbus_get_property(self, prop, member, proxy):
        return proxy.Get(
            self.NM + '.' + member,
            prop,
            dbus_interface='org.freedesktop.DBus.Properties')

    def repopulate_ap_list(self):
        apl = []
        res = []
        for i in self.devlist:
            tmp = self.bus.get_object(self.NM, i)
            if self.dbus_get_property('DeviceType', 'Device', tmp) == 2:
                apl.append(
                    self.bus.get_object(self.NM, i) .GetAccessPoints(
                        dbus_interface=self.NM + '.Device.Wireless'))
        for i in apl:
            for j in i:
                res.append(self.bus.get_object(self.NM, j))
        return res

    def get_ssid_string(self, ssid):
        if is_python_3():
            return b"".join([b"%s" % k.to_bytes(1, "little") for k in ssid]).decode('utf-8')
        else:
            return b"%s" % bytearray(ssid).decode('utf-8')

    def form_rssi_dic(self):
        for i in self.repopulate_ap_list():
            ssid = self.dbus_get_property('Ssid', 'AccessPoint', i)
            strength = self.dbus_get_property('Strength', 'AccessPoint', i)
            self.rssid[self.get_ssid_string(ssid)] = int(strength)

    def plotter(self):
        try:
            plt
        except NameError:
            log.error(
                "was unable to use plotting library, try setting up one of: ")
            log.error(
                ("matplotlib (pip install matplotlib)\n"
                 "python-tk (sudo apt-get install python-tk)\n"))
        else:
            graphs = []
            for i in self.data:
                graphs.append(plt.plot(self.xaxis, self.data[i], label=i))
            plt.xlabel("Seconds")
            plt.ylabel("RSSI, %")
            plt.legend(handles=[g[0] for g in graphs])
            plt.show()

    def handle_rssi_change(self, *_):
        self.form_rssi_dic()
        self.xaxis.append(time.time() - self.start_time)
        for i in [x for x in self.watched if x in self.rssid]:
            if i in self.data.keys():
                self.data[i].append(self.rssid[i])
            else:
                self.data[i] = []
                self.data[i].append(self.rssid[i])
        return True

    def iowch(self, _arg, _key, loop):
        cmd = sys.stdin.readline()
        if cmd.startswith("stop"):
            print('stopping the program')
            loop.quit()
            return False
        elif cmd.startswith("print"):
            print(self.__repr__())
        elif cmd.startswith("plot"):
            print('plotting your rssi data')
            self.plotter()
        return True

if __name__ == '__main__':
    broker="broker.hivemq.com"
    client = mqtt.Client()
    client.connect(broker, 1883)
    client.on_message = on_message

    parser = argparse.ArgumentParser()
    parser.add_argument("-i",
                        "--interactive",
                        help="start polling RSSI from the networks",
                        action="store_true")
    parser.add_argument("-n",
                        "--networks",
                        nargs="*",
                        help="networks to collect data from",
                        default=[])
    args = parser.parse_args()
    wifi_dict = {}
    loop = gobject.MainLoop()
    DBusGMainLoop(set_as_default=True)
    wfl = WiFiList(args.networks)
    wfl.form_rssi_dic()
    gobject.io_add_watch(sys.stdin, glib.IO_IN, wfl.iowch, loop)
    #print(wfl.__repr__())
    if args.interactive:
        loop.run()
  
    # Publish to Node RED
    print("Publishing...")
    wifi_dict = wfl.get_wifi_dict()
    max_value = max(wifi_dict.values())
    print("RSSI: %d" % max_value)
    client.publish("wifi/RSSI", "%d" % max_value)
    max_key = None
    max_key = [k for k, v in wifi_dict.items() if v == max_value]
    client.publish("wifi/SSID", "Strongest wifi signal is from: %s" % max_key)
    client.disconnect()

"""
This module is a wrapper for the D-Bus bluetooth implementation.
"""

import os
import time

import dbus
from dbus.mainloop.glib import DBusGMainLoop

import gobject

# try:
# 	from gi.repository import GObject
# except:
# 	print "cepe GObject"

# ref: http://stackoverflow.com/a/1796638
#gobject.GObject.threads_init()

try:
	import xbmc, xbmcplugin, xbmcgui, xbmcaddon

except ImportError as err:
	#log.warning("%s - using 'debug.XBMC*'-modules instead" % err.message)
	import debug.xbmc as xbmc
	import debug.xbmcgui as xbmcgui
	import debug.xbmcaddon as xbmcaddon

__author__ = 'lars'
__addon__		= xbmcaddon.Addon()
__addonname__	= __addon__.getAddonInfo('name')
__addonpath__	= __addon__.getAddonInfo('path')


class BluetoothHandler(object):

	"""
	Based on "/usr/bin/bluez-test-*.py"
	"""

	def __init__(self, dev_found_callback):

		self.dev_found_callback = dev_found_callback
		#self.dev_found_callback = self.device_found

		# attach a main loop for asynchronuous calls
		#dbus_mainloop = DBusGMainLoop(set_as_default=True)
		dbus_mainloop = DBusGMainLoop()

		# use session bus?
		# http://askubuntu.com/a/138150
		# bus = dbus.SessionBus(mainloop=dbus_mainloop)
		# obj = bus.add_signal_receiver(callback, signal_name="DeviceFound", dbus_interface="org.bluez.Adapter", bus_name="org.bluez", path="/")

		# initialize D-Bus objects
		bus = dbus.SystemBus(mainloop=dbus_mainloop)

		manager = dbus.Interface(bus.get_object("org.bluez", "/"), "org.bluez.Manager")
		adapter = dbus.Interface(bus.get_object("org.bluez", manager.DefaultAdapter()), "org.bluez.Adapter")

		# initialize D-bus callbacks (for scan devices, and more)
		#bus.add_signal_receiver(self.dev_found_callback, dbus_interface="org.bluez.Adapter", signal_name="DeviceFound")
		#bus.add_signal_receiver(self._property_changed, dbus_interface="org.bluez.Adapter", signal_name="PropertyChanged")


		adapter.connect_to_signal("DeviceFound", self.dev_found_callback)
		adapter.connect_to_signal("PropertyChanged", self._property_changed)

		# store objects
		self._stop = False
		self.bus = bus
		self.manager = manager
		self.adapter = adapter
		self.network = None

	def run(self):
		"""
		Run the gobject event loop
		"""

		# Don't use loop.run() because Python's GIL will block all threads
		loop = gobject.MainLoop()
		context = loop.get_context()
		while not self._stop:
			if context.pending():
				context.iteration( True )
			else:
				time.sleep(1)

	def stop(self):
		"""
		Stop the gobject event loop
		"""
		self._stop = True

	def scan_devices(self):

		# start scan
		self.adapter.StartDiscovery()

		# start mainloop
		# Ref: https://github.com/notspiff/kodi-cmake/blob/master/tools/EventClients/lib/python/zeroconf.py#L79
		#self.mainloop.run()
		self.run()

	def device_found(self, addr, prop):

		for key in prop.keys():
			value = prop[key]
			if type(value) is dbus.String:
				value = unicode(value).encode('ascii', 'replace')
			if (key == "Class"):
				print("    %s = 0x%06x" % (key, value))
			else:
				print("    %s = %s" % (key, value))

	def _property_changed(self, name, value):

		if name == "Discovering" and not value:
			print("bye!")
			#self.mainloop.quit()
			self.stop()

	def pair_devices(self):
		pass

	def explore_services(self, addr="all"):
		# list service: "sdptool browse"
		# or "bluez-test-device discover <address>

		#services = bluetooth.find_service(address=addr)
		pass


	def connect_nap(self, device):

		# get device path
		device = self.adapter.FindDevice(device)

		# get network object
		self.network = dbus.Interface(self.bus.get_object("org.bluez", device), "org.bluez.Network")

		# connect. Returns adapter name
		iface = self.network.Connect("nap")

		print(unicode(iface).encode('ascii', 'replace'))

		return iface
		# configure device to get ip-address from DHCP
		# (sudo ifconfig bnep0 up)??
		# run os.system: sudo dhclient bnep0

	def disconnect_nap(self):

		self.network.Disconnect()


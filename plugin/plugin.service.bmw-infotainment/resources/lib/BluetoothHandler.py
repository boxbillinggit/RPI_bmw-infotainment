"""
Bluetooth service extension.
"""

import BluetoothHandler

__author__ = 'Lars'


def generate_list(devices):
	for addr, name in devices:
		print("  %s - %s" % (addr, name))


class BTService(object):

	def __init__(self):
		self.devices = []

		pass

	def scan_devices(self):
		self.devices = BluetoothHandler.discover_devices(lookup_names = True)
		generate_list(self.devices)

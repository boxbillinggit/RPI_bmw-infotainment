__author__ = 'Lars'

import os

class Addon(object):

	def __init__(self):
		self.mem = {"gateway.ip-address": "169.254.0.1", "gateway.port": "4287"}
		self.addon_info = {"name": "XBMC BMW addon", "id": "script.ibus.bmw", "path": os.getcwd()}

	def getSetting(self, setting):

		buf = raw_input("'%s' [%s] >> " % (setting, self.mem.get(setting)))

		if buf:
			# user wrote something, save setting and return
			self.mem.update({setting: buf})
			return buf
		else:
			return self.mem.get(setting)

	def setSetting(self, setting, status):
		self.mem.update({setting: status})

		print("'%s': %s" % (setting, status))

	def getAddonInfo(self, id):
		return self.addon_info.get(id, "not defined")

	def openSettings(self):
		pass
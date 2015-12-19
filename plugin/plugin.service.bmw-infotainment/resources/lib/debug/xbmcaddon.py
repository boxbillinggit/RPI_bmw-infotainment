__author__ = 'Lars'

import os

settings = {"gateway.ip-address": "127.0.0.1", "gateway.port": "4287"}

ADDON_ID = "plugin.service.bmw-infotainment"
ADDON_PATH = os.path.join(os.path.expanduser("~"), ".kodi/addons", ADDON_ID)

addon = {
	"name": 	"XBMC BMW addon",
	"id": 		ADDON_ID,
	"path": 	ADDON_PATH
}


# special for test-scripts to catch events executed in XBMC/KODI. This will be overriden
# from test-script. so without test-script just print to console.
def emit(src="unknown", args=None):
	print("{}: \"{}\"".format(src, args))


class Addon(object):

	def __init__(self):
		pass


	def getSetting(self, setting):

		buf = raw_input("'%s' [%s] >> " % (setting, settings.get(setting)))

		if buf:
			# user wrote something, save setting and return
			settings.update({setting: buf})
			return buf
		else:
			return settings.get(setting)

	def setSetting(self, setting, status):
		settings.update({setting: status})

		emit(src="{}.{}.setSetting".format(__name__, self.__class__.__name__), args="{}: {}".format(setting, status))

	def getAddonInfo(self, id):
		return addon.get(id, "not defined")

	def openSettings(self):
		pass
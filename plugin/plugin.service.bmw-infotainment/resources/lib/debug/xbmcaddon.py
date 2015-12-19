__author__ = 		'Lars'
__modulename__ = 	"xbmcaddon"

import os
import events

# can be overriden from test-script
event = events.Debug()


ADDON_ID = "plugin.service.bmw-infotainment"
ADDON_PATH = os.path.join(os.path.expanduser("~"), ".kodi/addons", ADDON_ID)

settings = {
	"gateway.ip-address": "127.0.0.1",
	"gateway.port": "4287"
}

addon = {
	"name": 	"XBMC BMW addon",
	"id": 		ADDON_ID,
	"path": 	ADDON_PATH
}


class Addon(object):

	def __init__(self):
		pass


	def getSetting(self, setting):

		buf = event.user_input(module=__modulename__, method="%s.getSetting" % self.__class__.__name__, args=setting, default=settings.get(setting))

		if buf:
			# user wrote something, save setting and return
			settings.update({setting: buf})
			return buf
		else:
			return settings.get(setting)

	def setSetting(self, setting, status):
		settings.update({setting: status})

		event.emit(module=__modulename__, method="%s.setSetting" % self.__class__.__name__, args="{}: {}".format(setting, status))

	def getAddonInfo(self, id):
		return addon.get(id, "ERROR - not defined in '%s'" % __name__)

	def openSettings(self):
		pass

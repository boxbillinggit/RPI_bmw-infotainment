"""
This module is a constructor, returning a function for events against XBMC/KODI.

Reference:
http://kodi.wiki/view/List_of_Built_In_Functions
http://kodi.wiki/view/keymap#Actions
http://kodi.wiki/view/Action_IDs
"""

import settings
import time

try:
	import xbmc, xbmcgui, xbmcaddon

except ImportError as err:
	import debug.xbmc as xbmc
	import debug.xbmcgui as xbmcgui
	import debug.xbmcaddon as xbmcaddon

__author__ 		= 'Lars'
__monitor__ 	= xbmc.Monitor()
__addon__		= xbmcaddon.Addon()
__addonid__		= __addon__.getAddonInfo('id')


def action(event):

	"""
	Factory function returning a executable action in XBMC/KODI. When scrolling
	we must handle different speeds, hence *args is forwarded to method
	"""

	return lambda *args: _action(event, *args)


def _action(event, *args):

	"""
	Execute an action on XBMC/KODI.
	"""

	repeat = int(args[0]) if args else 1

	for n in range(repeat):

		if n > 0:
			time.sleep(settings.Buttons.SCROLL_SPEED)

		xbmc.executebuiltin("Action(%s)" % event)


def shutdown():

	# xbmc.shutdown()
	xbmc.executebuiltin("Quit")


def notify_disconnected(attempts):
	dialog = xbmcgui.Dialog()
	dialog.notification(__addonid__, "Connection lost, reconnecting... ({} of {})".format(attempts, settings.TCPIP.MAX_ATTEMPTS))


class AddonSettings(object):

	"""
	Class for plugin settings.
	"""

	TEXT 	= "welcome-text"
	BUS_STS	= "gateway.bus-activity"
	STATUS 	= "gateway.status"
	ADDRESS = "gateway.ip-address"
	PORT 	= "gateway.port"

	@staticmethod
	def get_welcome_text():
		addon = xbmcaddon.Addon()
		return addon.getSetting(AddonSettings.TEXT)

	@staticmethod
	def set_status(state):
		__addon__.setSetting(AddonSettings.STATUS, state.capitalize())

	@staticmethod
	def set_bus_activity(percent):
		__addon__.setSetting(AddonSettings.BUS_STS, "{:.2%}".format(percent))

	def __init__(self):
		self.address = None
		self.port = None

	def get_host(self):

		addon = xbmcaddon.Addon()
		self.address = addon.getSetting(AddonSettings.ADDRESS)
		self.port = int(addon.getSetting(AddonSettings.PORT))

		return self.address, self.port

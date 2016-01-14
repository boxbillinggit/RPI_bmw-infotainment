"""
This module is a constructor, returning a function for events against XBMC/KODI.

Reference:
http://kodi.wiki/view/List_of_Built_In_Functions
http://kodi.wiki/view/keymap#Actions
http://kodi.wiki/view/Action_IDs
"""

import time
import log as log_module
log = log_module.init_logger(__name__)

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

	WAIT = 0.1

	repeat = int(args[0]) if args else 1

	for n in range(repeat):

		if n > 0:
			time.sleep(WAIT)

		xbmc.executebuiltin("Action(%s)" % event)


def notification(msg):
	dialog = xbmcgui.Dialog()
	dialog.notification(__addonid__, msg)


class TCPIPSettings(object):

	"""
	Class containing the Interface against XBMC/KODI TCP/IP plugin settings.
	"""

	STATUS = "gateway.status"
	ADDRESS = "gateway.ip-address"
	PORT = "gateway.port"

	def __init__(self):
		self.address = None
		self.port = None

	def set_status(self, ident, status):
		__addon__.setSetting(ident, status)

	def get_status(self, ident):
		addon = xbmcaddon.Addon()
		return addon.getSetting(ident)

	def get_host(self):

		addon = xbmcaddon.Addon()
		self.address = addon.getSetting(TCPIPSettings.ADDRESS)
		self.port = int(addon.getSetting(TCPIPSettings.PORT))

		return self.address, self.port

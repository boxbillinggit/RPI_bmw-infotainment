"""
This module is a constructor, returning a function for events against XBMC/KODI.

Reference:
http://kodi.wiki/view/List_of_Built_In_Functions
http://kodi.wiki/view/keymap#Actions
http://kodi.wiki/view/Action_IDs
"""

import log as log_module
log = log_module.init_logger(__name__)

try:
	import xbmc, xbmcplugin, xbmcgui, xbmcaddon

except ImportError as err:
	import debug.xbmc as xbmc
	import debug.xbmcgui as xbmcgui
	import debug.xbmcaddon as xbmcaddon

__author__ 		= 'Lars'
__monitor__ 	= xbmc.Monitor()
__addon__		= xbmcaddon.Addon()
__addonid__		= __addon__.getAddonInfo('id')


def action(arg):

	# construct a method by returning a function.
	return lambda: xbmc.executebuiltin("Action(%s)" % arg)


# TODO: have this here?
class TCPIPSettings(object):

	"""
	Interface against XBMC/KODI.
	"""

	STATUS = "gateway.status"
	HOST = "gateway.ip-address"
	PORT = "gateway.port"

	def __init__(self):
		pass

	def set_status(self, ident, status):
		__addon__.setSetting(ident, status)

	def get_status(self, ident):
		addon = xbmcaddon.Addon()
		return addon.getSetting(ident)

	def get_host(self):
		addon = xbmcaddon.Addon()
		return addon.getSetting(TCPIPSettings.HOST), int(addon.getSetting(TCPIPSettings.PORT))

	def get_address(self):
		addon = xbmcaddon.Addon()
		return addon.getSetting(TCPIPSettings.HOST)

	def get_port(self):
		addon = xbmcaddon.Addon()
		return int(addon.getSetting(TCPIPSettings.PORT))

	def notify_disconnected(self, msg):
		dialog = xbmcgui.Dialog()
		dialog.notification(__addonid__, msg)

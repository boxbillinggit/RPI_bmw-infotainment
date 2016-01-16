"""
This module is a constructor, returning a function for events against XBMC/KODI.

Reference:
http://kodi.wiki/view/List_of_Built_In_Functions
http://kodi.wiki/view/keymap#Actions
http://kodi.wiki/view/Action_IDs
"""

import settings
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

	repeat = int(args[0]) if args else 1

	for n in range(repeat):

		if n > 0:
			time.sleep(settings.Buttons.SCROLL_SPEED)

		xbmc.executebuiltin("Action(%s)" % event)


def notification(msg):
	dialog = xbmcgui.Dialog()
	dialog.notification(__addonid__, msg)


def shutdown():

	# xbmc.shutdown()
	xbmc.executebuiltin("Quit")


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


class System(object):

	"""
	Interface for controlling system shutdown, etc
	"""

	SHUTDOWN, INIT = range(2)

	def __init__(self, scheduler):
		self.state = System.INIT
		self.scheduler = scheduler

	def state_init(self):

		""" Driver came back within time, abort shutdown """

		if self.state == System.SHUTDOWN:
			self.scheduler.remove(shutdown)
			log.info("{} - Welcome back! (Aborting system shutdown request)".format(self.__class__.__name__))

		self.state = System.INIT

	def state_shutdown(self):
		""" Schedule shutdown when key has been pulled out from ignition lock """

		if self.state == System.INIT:
			self.scheduler.add(shutdown, timestamp=time.time()+settings.System.IDLE_SHUTDOWN)
			log.info("{} - System shutdown is scheduled within {} min".format(self.__class__.__name__, (settings.System.IDLE_SHUTDOWN/60)))

		self.state = System.SHUTDOWN

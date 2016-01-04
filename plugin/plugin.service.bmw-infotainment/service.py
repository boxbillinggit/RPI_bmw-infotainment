"""
This is a service add'on for XBMC/KODI

References:
http://kodi.wiki/view/Service_addons
Python dev docs - http://mirrors.kodi.tv/docs/python-docs/14.x-helix/
"""

import resources.lib.log as logger
log = logger.init_logger(__name__)

try:
	import xbmc, xbmcplugin, xbmcgui, xbmcaddon

except ImportError as err:
	log.warning("%s - using 'debug.XBMC'-modules instead" % err.message)
	import resources.lib.debug.xbmc as xbmc
	import resources.lib.debug.xbmcgui as xbmcgui
	import resources.lib.debug.xbmcaddon as xbmcaddon

__author__ 		= 'Lars'
__monitor__ 	= xbmc.Monitor()
__addon__		= xbmcaddon.Addon()
__addonname__	= __addon__.getAddonInfo('name')
__addonid__		= __addon__.getAddonInfo('id')

import resources.lib.settings as settings
from resources.lib.event_handler import EventHandler
from resources.lib.tcp_handler import TCPIPHandler
from resources.lib.gui_events import Callback

if settings.DEBUGGER_ON:

	dialog = xbmcgui.Dialog()
	dialog.notification(__addonid__,"Python debugger on, waiting for connection ({}s)...").format(settings.DEBUGGER_TIMEOUT)

	import rpdb2
	rpdb2.start_embedded_debugger('pw', timeout=settings.DEBUGGER_TIMEOUT)

events = EventHandler()
tcp_service = TCPIPHandler()

# init callbacks from GUI. pass service methods for constructing callbacks.
callback = Callback(tcp_service)


if __name__ == "__main__":

	# set callbacks
	callback.init_callbacks()

	events.start()

	# init and start the TCP/IP service thread...
	tcp_service.start()

	# ...and wait for XBMC/KODI to exit!
	if __monitor__.waitForAbort():

		# perform necessary shutdowns (stop threads, and more...)
		log.info("Bye!")

		# Close socket gracefully (XBMC/KODI waits for thread to finish before it closes down)
		tcp_service.request_stop()

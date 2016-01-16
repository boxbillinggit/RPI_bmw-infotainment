"""
This is the service add'on for XBMC/KODI

References:
http://kodi.wiki/view/Service_addons
Python dev docs - http://mirrors.kodi.tv/docs/python-docs/14.x-helix/
"""

import resources.lib.settings as settings
import resources.lib.log as logger
import resources.lib.libguicallback as guicallback

from resources.lib.signal_methods import KombiInstrument
from resources.lib.event_handler import EventHandler
from resources.lib.tcp_handler import TCPIPHandler

log = logger.init_logger(__name__)

try:
	import xbmc, xbmcgui, xbmcaddon

except ImportError as err:
	log.warning("%s - using debug-modules instead" % err.message)
	import resources.lib.debug.xbmc as xbmc
	import resources.lib.debug.xbmcgui as xbmcgui
	import resources.lib.debug.xbmcaddon as xbmcaddon

__author__ 		= 'Lars'
__monitor__ 	= xbmc.Monitor()
__addon__		= xbmcaddon.Addon()
__addonname__	= __addon__.getAddonInfo('name')
__addonid__		= __addon__.getAddonInfo('id')


if settings.WinPDB.ACTIVE:

	dialog = xbmcgui.Dialog()
	dialog.notification(__addonid__, "Debugger on, waiting for connection ({}s)...").format(settings.WinPDB.TIMEOUT)

	import rpdb2
	rpdb2.start_embedded_debugger('pw', timeout=settings.WinPDB.TIMEOUT)

event_handler = EventHandler()
tcp_service = TCPIPHandler()


def launch_initial_events():

	"""
	Initial events launched when system is started!
	"""

	kombi_instrument = KombiInstrument(tcp_service.send)
	kombi_instrument.set_text(__addon__.getSetting("welcome-text"))


def set_callbacks():

	"""
	cPython library "libguicallback.so" acts as an interface between script(GUI)
	and service module, allowing callbacks from GUI to interact with service-module.
	"""

	guicallback.setOnConnect(tcp_service.request_start)
	guicallback.setOnDisconnect(tcp_service.request_stop)

if __name__ == "__main__":

	set_callbacks()

	event_handler.start()

	tcp_service.start()

	launch_initial_events()

	if __monitor__.waitForAbort():

		log.info("Bye!")

		# Close socket gracefully (XBMC/KODI waits for thread to finish before it closes down)
		tcp_service.request_stop()

"""
This is the service add-on for XBMC/KODI

References:
http://kodi.wiki/view/Service_addons
Python dev docs - http://mirrors.kodi.tv/docs/python-docs/14.x-helix/
"""
import resources.lib.winpdb as winpdb
import resources.lib.kodi as kodi
import resources.lib.log as logger
import resources.lib.libguicallback as guicallback

from resources.lib.bmw import KombiInstrument
from resources.lib.event_handler import EventHandler
from resources.lib.tcp_handler import TCPIPHandler

log = logger.init_logger(__name__)

try:
	import xbmc
except ImportError as err:
	log.warning("%s - using debug-modules instead" % err.message)
	import resources.lib.debug.xbmc as xbmc

__author__ 		= 'Lars'
__monitor__ 	= xbmc.Monitor()

winpdb.launch_debugger()

event_handler = EventHandler()
tcp_service = TCPIPHandler()


def launch_initial_events():

	"""
	Initial events launched when system is started!
	"""

	kombi_instrument = KombiInstrument(tcp_service.send, tcp_service.filter.events)
	kombi_instrument.welcome_text(kodi.AddonSettings.get_welcome_text())


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

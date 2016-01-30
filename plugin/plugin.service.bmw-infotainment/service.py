"""
This is the service add-on for XBMC/KODI

References:
http://kodi.wiki/view/Service_addons
http://mirrors.kodi.tv/docs/python-docs/14.x-helix/
"""
import resources.lib.winpdb as winpdb
import resources.lib.log as logger

from resources.lib.kodi import gui, __monitor__
from resources.lib.main_thread import MainThread
from resources.lib.event_handler import EventHandler
from resources.lib.tcp_handler import TCPIPHandler

__author__ 		= 'Lars'

log = logger.init_logger(__name__)
winpdb.launch_debugger()


def still_alive():

	""" Run threads until abort is requested """

	return not __monitor__.abortRequested()


def handle_init():

	"""
	Start threads, launch initial events.
	"""

	event_thread.start()
	tcpip_thread.start()

	tcpip_thread.signal_handler.initialize_events()


def handle_shutdown():

	"""
	Perform necessary shutdowns (main-thread may be	blocked	with an open GUI)
	"""

	gui.close_all_windows()
	tcpip_thread.request_disconnect()


event_thread, tcpip_thread, main_thread = EventHandler(condition=still_alive, handle_exit=handle_shutdown), TCPIPHandler(condition=still_alive), MainThread(condition=still_alive)


if __name__ == "__main__":

	handle_init()

	# blocking until abort is requested (but may still be blocked from open GUI's)
	main_thread.start()

	log.info("Bye!")

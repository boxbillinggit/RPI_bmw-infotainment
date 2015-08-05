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
	import resources.lib.debug.XBMC as xbmc
	import resources.lib.debug.XBMCGUI as xbmcgui
	import resources.lib.debug.XBMCADDON as xbmcaddon

__author__ 		= 'Lars'
__monitor__ 	= xbmc.Monitor()
__addon__		= xbmcaddon.Addon()
__addonname__	= __addon__.getAddonInfo('name')
__addonid__		= __addon__.getAddonInfo('id')

# load all libraries
import resources.lib.settings as settings
from resources.lib.TCPIPHandler import TCPIPHandler
from resources.lib.callback import Callback

# start debug session with "WinPDB" console - if switch is turned on in "settings.py".
if settings.DEBUGGER_ON:

	# notify user that debugging is on
	dialog = xbmcgui.Dialog()
	dialog.notification("Python debugger on","Waiting for WinPDB (%ss)..." % settings.DEBUGGER_TIMEOUT)

	import rpdb2
	rpdb2.start_embedded_debugger('pw', timeout=settings.DEBUGGER_TIMEOUT)

# init the main service class
service = TCPIPHandler()

# init callbacks from GUI. pass service methods for constructing callbacks.
callback = Callback(service)

# Launch the service
if __name__ == "__main__":

	# set callbacks
	callback.init_callbacks()

	# init and start the TCP/IP service thread...
	service.start()

	# ...and wait for XBMC/KODI to exit!
	if __monitor__.waitForAbort():

		# perform necessary shutdowns (stop threads, and more...)
		log.info("Service add-on exits.")

		# Close socket gracefully (XBMC/KODI waits for thread to finish before it closes down)
		service.stop()

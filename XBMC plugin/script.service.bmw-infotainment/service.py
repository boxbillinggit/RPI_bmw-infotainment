__author__ = 'Lars'

# This is a service add'on for XBMC/KODI
# ref:  http://kodi.wiki/view/Service_addons
# Python dev docs: http://mirrors.kodi.tv/docs/python-docs/14.x-helix/

# load XBMC/KODI-specific modules
import xbmc, xbmcplugin, xbmcgui, xbmcaddon

__addon__		= xbmcaddon.Addon()
__addonname__	= __addon__.getAddonInfo('name')

# load all libraries
import resources.lib.settings as settings
from resources.lib.TCPhandler import TCPHandler
from resources.lib.callback import Callback

# start debug session with "WinPDB" console - if switch is turned on in "settings.py".
if settings.DEBUGGER_ON:

	# notify user that debugging is on
	dialog = xbmcgui.Dialog()
	dialog.notification("Python debugger on","Waiting for WinPDB (%ss)..." % settings.DEBUGGER_TIMEOUT)

	import rpdb2
	rpdb2.start_embedded_debugger('pw', timeout=settings.DEBUGGER_TIMEOUT)


# init XBMC/KODI monitor
monitor = xbmc.Monitor()

# init the main service class
service = TCPHandler()

# init callbacks from GUI. pass service methods for constructing callbacks.
callback = Callback(service)

# Launch the service
if __name__ == "__main__":

	# set callbacks
	callback.init_callbacks()

	# init and start the TCP service thread...
	service.start()

	# ...and wait for XBMC/KODI to exit!
	if monitor.waitForAbort():

		# perform necessary shutdowns (stop threads, and more...)
		xbmc.log("BMW: BMW-infotainment service exits. Bye!", level=xbmc.LOGINFO)

		# Close socket gracefully (XBMC/KODI waits for thread to finish before it closes down)
		service.stop()


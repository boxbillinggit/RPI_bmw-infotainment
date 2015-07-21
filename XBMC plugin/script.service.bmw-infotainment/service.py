__author__ = 'Lars'

# This is a service add'on for XBMC/KODI
# ref:  http://kodi.wiki/view/Service_addons

# Python dev docs: http://mirrors.kodi.tv/docs/python-docs/14.x-helix/
import xbmc, xbmcplugin, xbmcgui, xbmcaddon

# start debug session with "WinPDB" console - if switch is turned on in "settings.py".
if settings.DEBUGGER_ON:
	import rpdb2
	rpdb2.start_embedded_debugger('pw')

# load libs
#import resources.lib.debug as debug
import resources.lib.settings as settings
from resources.lib.TCPhandler import TCPHandler
from threading import Thread

__addon__		= xbmcaddon.Addon()
__addonname__	= __addon__.getAddonInfo('name')

# init XBMC/KODI monitor
monitor = xbmc.Monitor()

# init the main service class
service = TCPHandler()

# TCP service function.
def tcp_service():

	# Consider if we're terminating, otherwise just loop over again (restart connection).
	while service.attempts < settings.MAX_RECONNECT and not monitor.abortRequested():

		dialog = xbmcgui.Dialog()

		# ask user to reconnect (if not the first initial connection attempt)
		if service.attempts and not dialog.yesno(__addonname__, "Connection lost... (attempt: %s, host: %s:%s)" % (service.attempts, service.host, service.port), "Reconnect?" ):
			break

		# Init the TCP daemon -and handler. Blocks until disconnected...
		service.start()

	# the loop exited
	xbmc.log("BMW: service main loop stopped (function returns, thread terminates).", level=xbmc.LOGDEBUG)

if __name__ == "__main__":

	# launch the service thread...
	t = Thread(name='BMW-Service', target=tcp_service)
	t.daemon = True
	t.start()

	# ...and wait for XBMC/KODI to exit!
	if monitor.waitForAbort():

		# perform necessary shutdowns (stop threads, and more...)
		xbmc.log("BMW: BMW-infotainment service exits. Bye!", level=xbmc.LOGINFO)

		# Close socket gracefully (XBMC/KODI waits for thread to finish before it closes down)
		service.stop()


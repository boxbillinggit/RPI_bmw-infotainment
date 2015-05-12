__author__ = 'Lars'

# reference: http://kodi.wiki/view/HOW-TO:Automatically_start_addons_using_services

# enable DEBUG logging for kodi:
# http://kodi.wiki/view/Log_file/Advanced#Enable_debugging
# enter "settings -> system -> debugging"
# logfile is under "C:\Users\Lars\AppData\Roaming\Kodi"
# TODO implement SSH client for tesing OpenBM client https://github.com/paramiko/paramiko
import sys

# Python dev docs: http://mirrors.kodi.tv/docs/python-docs/14.x-helix/
import xbmc, xbmcplugin, xbmcgui, xbmcaddon

from threading import Thread
import asyncore
from resources.lib.TCPhandler import *

__addon__		= xbmcaddon.Addon()
__addonname__	= __addon__.getAddonInfo('name')

# some connection data
MAX_RECONNECT = 3

# init class
connection = MsgHandler()

# TCP server thread class.
def TCP_server():

	# Consider if we're terminating, otherwise just loop over again.
	# http://kodi.wiki/view/Service_addons
	# TODO: is monitor initialized at this stage? better solution required.
	# TODO: how to re-initialize a connection (from button in settings)? new thread? wake thread?
	while (connection.attempts < MAX_RECONNECT and not monitor.abortRequested()):

		connection.attempts += 1

		# Init the TCP connection class
		connection.start()

		xbmc.log("BMW: start asyncore loop")

		# blocking until disconnected..
		asyncore.loop()

		# inform user through a dialog
		dialog = xbmcgui.Dialog()
		if not dialog.yesno(__addonname__, "Connection lost... (host: %s:%s)" % (connection.host, connection.port), "reconnect?" ):
			break

		# reference: http://mirrors.kodi.tv/docs/python-docs/13.0-gotham/xbmc.html#-log
		xbmc.log("BMW: Connection lost... user (probably, if not shutting down) answered yes to re-connect (host: %s:%s)" % (connection.host, connection.port), level=xbmc.LOGDEBUG)


if __name__ == "__main__":
	monitor = xbmc.Monitor()

	# launch the server thread (daemon thread)...
	t = Thread( name='TCPServerThread', target=TCP_server)
	t.daemon = True
	t.start()

	# ...and wait for KODI to exit!
	if monitor.waitForAbort():

		# perform necessary shutdowns (stop threads, and more...)
		xbmc.log("BMW: bye!", level=xbmc.LOGDEBUG)

		# Close socket gracefully (KODI waits for thread to finish before it closes down)
		connection.stop()


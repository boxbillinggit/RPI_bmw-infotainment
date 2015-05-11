__author__ = 'Lars'

# reference: http://kodi.wiki/view/HOW-TO:Automatically_start_addons_using_services

# enable DEBUG logging for kodi:
# http://kodi.wiki/view/Log_file/Advanced#Enable_debugging
# enter "settings -> system -> debugging"
# logfile is under "C:\Users\Lars\AppData\Roaming\Kodi"
# TODO implement SSH client for tesing OpenBM client https://github.com/paramiko/paramiko
import sys

# Python dev docs: http://mirrors.kodi.tv/docs/python-docs/13.0-gotham/
import xbmc, xbmcplugin, xbmcgui, xbmcaddon

import threading
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

	while (connection.attempts < MAX_RECONNECT):

		connection.attempts += 1

		# Init the TCP connection class
		connection.start()

		xbmc.log("BMW: Try connecting... (host: %s:%s)" % (connection.host, connection.port))

		# blocking until disconnected..
		asyncore.loop()

		# inform user through a dialog
		dialog = xbmcgui.Dialog()
		if not dialog.yesno(__addonname__, "Connection lost... (host: %s:%s)" % (connection.host, connection.port), "Try to reconnect?" ):
			break

		# reference: http://mirrors.kodi.tv/docs/python-docs/13.0-gotham/xbmc.html#-log
		xbmc.log("BMW: Connection lost... (host: %s:%s)" % (connection.host, connection.port), level=xbmc.LOGDEBUG)


if __name__ == "__main__":
	monitor = xbmc.Monitor()

	# launch the server thread...
	threading.Thread( name='TCPServerThread', target=TCP_server ).start()

	# ...and wait for KODI to exit!
	if monitor.waitForAbort():

		# perform necessary shutdowns (stop threads, and more...)
		xbmc.log("BMW: bye!", level=xbmc.LOGDEBUG)

		# Close socket (graceful), then terminate thread (KODI waits for thread to finish before it closes down)
		# TODO: fix thread termination (and send disconnect message before terminating).
		connection.stop()


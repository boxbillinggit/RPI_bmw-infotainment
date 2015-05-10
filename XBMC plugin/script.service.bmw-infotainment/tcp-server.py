__author__ = 'Lars'

# reference: http://kodi.wiki/view/HOW-TO:Automatically_start_addons_using_services

# enable DEBUG logging for kodi:
# http://kodi.wiki/view/Log_file/Advanced#Enable_debugging
# enter "settings -> system -> debugging"
# logfile is under "C:\Users\Lars\AppData\Roaming\Kodi"

import sys

# Python dev docs: http://mirrors.kodi.tv/docs/python-docs/13.0-gotham/
import xbmc, xbmcplugin, xbmcgui, xbmcaddon

import time
import threading
import asyncore
from resources.lib.TCPhandler import *

__addon__		= xbmcaddon.Addon()
__addonname__	= __addon__.getAddonInfo('name')

# get host from settings
# reference: http://mirrors.kodi.tv/docs/python-docs/13.0-gotham/xbmcplugin.html#-getSetting
host = __addon__.getSetting("gateway.ip-address")
print "BMW: host from settings: %s" % host

# some connection data
# TODO: use a separate setting file?
HOST = '192.168.1.68'
PORT = 4287
RECONNECT = 3

connection = MsgHandler(HOST, PORT)


# TCP server thread class.
def TCP_server():

	while (connection.attempts < RECONNECT):

		connection.attempts += 1

		xbmc.log("BMW: Try connecting...")

		# Init the TCP connection class
		connection.start()

		# blocking until disconnected..
		asyncore.loop()

		# inform user through a dialog
		dialog = xbmcgui.Dialog()
		if not dialog.yesno(__addonname__, "Connection lost... Try to reconnect?"):
			break

		# reference: http://mirrors.kodi.tv/docs/python-docs/13.0-gotham/xbmc.html#-log
		xbmc.log("BMW: Connection lost...", level=xbmc.LOGDEBUG)


if __name__ == "__main__":
	monitor = xbmc.Monitor()

	# launch the server thread...
	threading.Thread( name='TCPServerThread', target=TCP_server ).start()

	# ...and wait for KODI to exit!
	if monitor.waitForAbort():

		# perform necessarry shutdowns (stop threads, and more...)
		xbmc.log("BMW: bye!", level=xbmc.LOGDEBUG)

		# Close socket (graceful), then terminate thread (KODI waits for thread to finish before it closes down)
		connection.stop()


__author__ = 'Lars'

import xbmc, xbmcplugin, xbmcgui, xbmcaddon
import bmwaddon

__addon__		= xbmcaddon.Addon()
__addonname__	= __addon__.getAddonInfo('name')

# http://stackoverflow.com/questions/4309607/whats-the-preferred-way-to-implement-a-hook-or-callback-in-python

# create callbacks (interface between script -and service module, supported by "bmwaddon.[dll/so/pyc]")
class Callback:

	def __init__(self, tcp_daemon):

		self.tcp_daemon = tcp_daemon

	# pass the callback functions to cPython extension
	def init_callbacks(self):

		# set callbacks
		bmwaddon.setOnConnect(self.tcp_daemon.start)
		bmwaddon.setOnDisconnect(self.tcp_daemon.stop)


	def callback_fcn(self):
		xbmc.log("BMW: a callback!!!!!!!!!!")
		dialog = xbmcgui.Dialog()
		dialog.ok(__addonname__, "hello there callback")

	def on_connect(self):
		pass

	def on_disconnect(self):
		pass

#previous located in "service.py" but didn't work
# attach handlers for settings in button
# class GUICallback(xbmcgui.Window):
#
# 	# ref: http://kodi.wiki/view/Window_IDs
# 	SETTINGS_GUI_ID = 10140
#
# 	def __init__(self, *args, **kwargs ):
# 		xbmc.log("BMW: SETTINGS: init class")
#
#
# 		# fetch the GUI settings window
# 		#self.gui_win = xbmcgui.Window()
#
# 		# init class TODO: needed?
# 		xbmcgui.Window.__init__(self)
#
# 	# listen to all click events for window
# 	def onClick(self, id):
# 		xbmc.log("BMW: SETTINGS: clicked on id %s" % id)
#
# 	def onInit(self):
# 		# TODO: disable button when connected resp. disconnected (cant do such action if window isn't open)
# 		xbmc.log("BMW: SETTINGS: init window")
#
#
# # create window object for button callback.
# button = GUICallback(10140)
#

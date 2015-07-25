__author__ = 'Lars'
# This module acts as a supporting interface between script -and service module, implemented in "bmwaddon.[dll/so/pyc]"
# TODO: rename module?

import xbmc, xbmcplugin, xbmcgui, xbmcaddon
import bmwaddon

__addon__		= xbmcaddon.Addon()
__addonname__	= __addon__.getAddonInfo('name')

# create callbacks
class Callback:

	def __init__(self, service):

		self.service = service

	# pass the callback functions to cPython extension
	def init_callbacks(self):

		# set callbacks
		bmwaddon.setOnConnect(self.service.start)
		bmwaddon.setOnDisconnect(self.service.stop)

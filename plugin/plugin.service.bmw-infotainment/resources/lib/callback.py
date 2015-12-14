"""
This module acts as a supporting interface between script -and service module, implemented in "bmwaddon.[dll/so/pyc]"
"""

import log as logger
log = logger.init_logger(__name__)

try:
	# Python dev docs: http://mirrors.kodi.tv/docs/python-docs/14.x-helix/
	import xbmc, xbmcplugin, xbmcgui, xbmcaddon

except ImportError as err:
	log.warning("%s - using 'debug.XBMC'-modules instead" % err.message)
	import resources.lib.debug.xbmc as xbmc
	import resources.lib.debug.xbmcgui as xbmcgui
	import resources.lib.debug.xbmcaddon as xbmcaddon

import libguicallback as guicallback

__author__ = 'Lars'
__addon__		= xbmcaddon.Addon()
__addonname__	= __addon__.getAddonInfo('name')


# create callbacks
class Callback(object):

	def __init__(self, service):

		self.service = service

	# pass the callback functions to cPython extension
	def init_callbacks(self):

		# set callbacks
		guicallback.setOnConnect(self.service.start)
		guicallback.setOnDisconnect(self.service.stop)

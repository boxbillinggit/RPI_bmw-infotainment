"""
Global settings for this add-on
"""

import os

try:
	import xbmc, xbmcplugin, xbmcgui, xbmcaddon

except ImportError as err:
	#log.warning("%s - using 'debug.XBMC*'-modules instead" % err.message)
	import debug.xbmc as xbmc
	import debug.xbmcgui as xbmcgui
	import debug.xbmcaddon as xbmcaddon

__author__ = 'lars'
__addon__		= xbmcaddon.Addon()
__addonname__	= __addon__.getAddonInfo('name')
__addonpath__	= __addon__.getAddonInfo('path')


# use debugger
DEBUGGER = False

# Paths
path = {
	"xml-template-path": os.path.join(__addonpath__, "resources", "data"),
	"lib": os.path.join(__addonpath__, "resources", "lib"),
}

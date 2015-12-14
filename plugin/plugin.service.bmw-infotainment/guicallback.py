"""
This module act as default handler for XBMC/KODI command "RunScript()"
"""

try:
	import xbmc, xbmcplugin, xbmcgui, xbmcaddon

except ImportError as err:
	import debug.XBMC as xbmc
	import debug.XBMCGUI as xbmcgui
	import debug.XBMCADDON as xbmcaddon

__author__ 		= 'Lars'
__addon__		= xbmcaddon.Addon()
__addonname__	= __addon__.getAddonInfo('name')

import sys
import resources.lib.libguicallback as guicallback

action = {
	"connect": guicallback.onConnect,
	"disconnect": guicallback.onDisconnect
}

# script is called with an argument
if len(sys.argv) > 1:

	# get first argument passed from XBMC/KODI GUI and select action
	callback = action.get(sys.argv[1])

	# execute action
	if callback and hasattr(callback, "__call__"):
		callback()

else:
	# Default action: pop settings when launching script without any arguments
	__addon__.openSettings()

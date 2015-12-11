"""
This module act as default handler for XBMC/KODI command "RunScript()"
"""

import resources.lib.log as logger
log = logger.init_logger(__name__)

try:
	import xbmc, xbmcplugin, xbmcgui, xbmcaddon

except ImportError as err:
	log.warning("%s - using 'debug.XBMC'-modules instead" % err.message)
	import debug.XBMC as xbmc
	import debug.XBMCGUI as xbmcgui
	import debug.XBMCADDON as xbmcaddon

__author__ 		= 'Lars'
__addon__		= xbmcaddon.Addon()
__addonname__	= __addon__.getAddonInfo('name')

import sys
import resources.lib.libguicallback as guicallback

# action selector based on argument passed from XBMC/KODI GUI
select_action = {
	"connect": guicallback.onConnect,
	"disconnect": guicallback.onDisconnect
}

# script is called with an argument
if len(sys.argv) > 1:

	# get the argument passed from XBMC/KODI GUI
	arg = sys.argv[1]

	# get action
	exec_action = select_action[arg]

	# execute action
	exec_action()

else:
	# Default action: pop settings when launching script without arguments
	__addon__.openSettings()

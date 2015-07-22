__author__ = 'Lars'
# This module act as default handler for XBMC/KODI command "RunScript()"

import sys

# Python dev docs: http://mirrors.kodi.tv/docs/python-docs/14.x-helix/
import xbmc, xbmcplugin, xbmcgui, xbmcaddon
import resources.lib.bmwaddon as bmwaddon

__addon__		= xbmcaddon.Addon()
__addonname__	= __addon__.getAddonInfo('name')

# action selector based on argument passed from XBMC/KODI GUI
select_action = {
	"connect": bmwaddon.onConnect,
	"disconnect": bmwaddon.onDisconnect
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

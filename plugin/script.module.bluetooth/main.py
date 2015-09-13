"""
This module act as default handler for XBMC/KODI command "RunScript()"
"""

import sys
import resources.lib.gui as gui
import resources.lib.settings as settings

try:
	import xbmc, xbmcplugin, xbmcgui, xbmcaddon

except ImportError as err:
	print("fel")

__author__ = 'lars'
__addon__		= xbmcaddon.Addon()
__addonname__	= __addon__.getAddonInfo('name')

# start debugger
if settings.DEBUGGER:
	import rpdb2
	rpdb2.start_embedded_debugger('pw')

# action selector based on argument passed from XBMC/KODI GUI
select_action = {
	"connect": None,
	"disconnect": None
}


if __name__ == "__main__":

	# script is called with an argument
	if len(sys.argv) > 1:

		# get the argument passed from XBMC/KODI GUI
		arg = sys.argv[1]

		# get action
		action = select_action.get(arg)

		# execute action (if we found one)
		if hasattr(action, "__call__"):
			action()
		else:
			pass
			# No action found


	else:
		# No arguments passed to script

		# just open tjhe window
		gui.init_window("bluetooth-home.xml")
		#gui.init_window("MyProgams-custom.xml")
		#gui.init_window("DialogPeripheralManager-custom.xml")


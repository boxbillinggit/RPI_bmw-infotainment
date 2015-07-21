__author__ = 'Lars'

import sys

# Python dev docs: http://mirrors.kodi.tv/docs/python-docs/14.x-helix/
import xbmc, xbmcplugin, xbmcgui, xbmcaddon

__addon__		= xbmcaddon.Addon()
__addonname__	= __addon__.getAddonInfo('name')

# default handler for "RunScript()"
# good to know: http://kodi.wiki/view/List_of_built-in_functions
# http://kodi.wiki/view/List_of_boolean_conditions

try:
	# get the argument (if exists)
	arg = sys.argv[1]

	dialog = xbmcgui.Dialog()
	dialog.yesno(__addonname__, "Request to \"%s\" is not available at the moment." % arg )
	xbmc.log("BMW: dialog in execute script. with argument \"%s\"" % arg )

except IndexError:

	# pop settings when launching script without arguments
	__addon__.openSettings()


# TODO: when executing script, we get a new thread. must find method to call




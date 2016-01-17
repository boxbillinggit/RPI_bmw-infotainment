"""
Reference: http://kodi.wiki/view/HOW-TO:Debug_python_scripts_with_WinPDB
"""

import settings

try:
	import xbmcgui, xbmcaddon
except ImportError as err:
	import debug.xbmcgui as xbmcgui
	import debug.xbmcaddon as xbmcaddon

__author__ 		= 'Lars'
__addon__		= xbmcaddon.Addon()
__addonid__		= __addon__.getAddonInfo('id')


def launch_debugger():

	if not settings.WinPDB.ACTIVE:
		return

	dialog = xbmcgui.Dialog()
	dialog.notification(__addonid__, "Debugger on, waiting for connection ({}s)...").format(settings.WinPDB.TIMEOUT)

	import rpdb2
	rpdb2.start_embedded_debugger('pw', timeout=settings.WinPDB.TIMEOUT)

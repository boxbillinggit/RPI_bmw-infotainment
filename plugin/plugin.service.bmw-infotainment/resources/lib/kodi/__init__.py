try:
	import xbmc
	import xbmcgui
	import xbmcaddon
	__DEBUG__ = False

except ImportError as err:
	import debug.xbmc as xbmc
	import debug.xbmcgui as xbmcgui
	import debug.xbmcaddon as xbmcaddon
	__DEBUG__ = True

__author__ 		= 'lars'
__xbmc__ 		= xbmc
__monitor__ 	= xbmc.Monitor()
__xbmcgui__		= xbmcgui
__xbmcaddon__	= xbmcaddon
__addon__		= xbmcaddon.Addon()
__addonid__		= __addon__.getAddonInfo('id')
__addonpath__	= __addon__.getAddonInfo('path')
__addonname__	= __addon__.getAddonInfo('name')

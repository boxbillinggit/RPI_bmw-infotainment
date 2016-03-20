from api import *

# TODO: import all kodi sub-modules here (doesn't need to import kodi, kodi.builtin, etc in module-level)

__author__ 		= 'lars'
__DEBUG__ 		= DEBUG
__xbmc__ 		= xbmc
__monitor__ 	= xbmc.Monitor()
__player__ 		= xbmc.Player()
__xbmcgui__		= xbmcgui
__xbmcaddon__	= xbmcaddon
__addon__		= xbmcaddon.Addon()
__addonid__		= __addon__.getAddonInfo('id')
__addonpath__	= __addon__.getAddonInfo('path')
__addonname__	= __addon__.getAddonInfo('name')

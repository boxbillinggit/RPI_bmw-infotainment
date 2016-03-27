""" Module for XBMC/KODI API """

__author__ = 'lars'

try:
	import xbmc
	import xbmcgui
	import xbmcaddon
	DEBUG = False

except ImportError as err:
	import debug.xbmc as xbmc
	import debug.xbmcgui as xbmcgui
	import debug.xbmcaddon as xbmcaddon
	DEBUG = True

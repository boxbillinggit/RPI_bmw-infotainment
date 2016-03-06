"""
Reference: http://kodi.wiki/view/HOW-TO:Debug_python_scripts_with_WinPDB
"""
import settings
from kodi import __xbmcgui__, __addonid__

__author__ = 'Lars'


def launch_debugger():

	if not settings.WinPDB.ACTIVE:
		return

	__xbmcgui__.Dialog().notification(__addonid__, "Debugger on, waiting for connection ({}s)...").format(settings.WinPDB.TIMEOUT)

	import rpdb2
	rpdb2.start_embedded_debugger('pw', timeout=settings.WinPDB.TIMEOUT)

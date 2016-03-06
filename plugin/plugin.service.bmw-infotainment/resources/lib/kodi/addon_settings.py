"""
Interface against KODI for all add-on settings.

NOTE: do not try to set settings when using different threads, etc. this will occasionally
lead to crashes with segmentation-faults, etc.. it doesn't matter if you handling setSettings
from same thread, it seems to not work anyway..
"""
from __init__ import __xbmcaddon__

__author__ = 'lars'

TEXT_WELCOME = "welcome-text"
TEXT_ENABLED = "welcome-text.enabled"
BUS_ACTIVITY = "gateway.bus-activity"
CONN_STATUS  = "gateway.status"
CONN_ADDRESS = "gateway.ip-address"
CONN_PORT    = "gateway.port"


def _get_setting(ident):

	""" Create new instance to read newest settings """

	return __xbmcaddon__.Addon().getSetting(ident)


def get_welcome_text():

	"""	Called from EventHandler-thread """

	if _get_setting(TEXT_ENABLED) == "true":
		return _get_setting(TEXT_WELCOME)


def get_host():

	""" Called from ThreadedSocket -or from GUI (dummy-thread)"""

	address = _get_setting(CONN_ADDRESS)
	port = int(_get_setting(CONN_PORT))

	return address, port

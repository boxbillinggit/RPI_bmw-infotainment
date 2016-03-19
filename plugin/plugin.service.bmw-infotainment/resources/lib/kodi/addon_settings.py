"""
Interface against KODI for all add-on settings.

NOTE: do not try to set settings when using different threads, etc. this will occasionally
lead to crashes with segmentation-faults, etc.. it doesn't matter if you handling setSettings
from same thread, it seems to not work anyway..
"""
from __init__ import __xbmcaddon__
from datetime import datetime, timedelta

__author__ = 'lars'

WELCOME_MSG_TEXT = "welcome-msg.text"
WELCOME_MSG_ACTV = "welcome-msg.enabled"
SYS_SHUTDOWN_TIME = "system-shutdown.time"
SYS_SHUTDOWN_ACTV = "system-shutdown.enabled"
GATEWAY_ADDR = "gateway.ip-address"
GATEWAY_PORT = "gateway.port"


def _get_setting(ident):

	""" Create new instance to read newest settings """

	return __xbmcaddon__.Addon().getSetting(ident)


def get_welcome_text():

	"""	Called from EventHandler-thread """

	if _get_setting(WELCOME_MSG_ACTV) == "true":
		return _get_setting(WELCOME_MSG_TEXT)


def get_host():

	""" Called from ThreadedSocket -or from GUI (dummy-thread)"""

	address = _get_setting(GATEWAY_ADDR)
	port = int(_get_setting(GATEWAY_PORT))

	return address, port


def schedule_shutdown():

	""" Setting for enabling shutdown on ignition-key out """

	if _get_setting(SYS_SHUTDOWN_ACTV) == "true":
		time = datetime.strptime(_get_setting(SYS_SHUTDOWN_TIME), "%H:%M")
		return timedelta(hours=time.hour, minutes=time.minute).seconds

	return None

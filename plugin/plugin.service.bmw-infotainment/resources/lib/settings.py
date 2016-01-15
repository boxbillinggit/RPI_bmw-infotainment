"""
All settings for this plugin
"""

import os
import logging

__author__ = 'Lars'


class WinPDB(object):

	""" Use Python Debugger with KODI """

	ACTIVE = False
	TIMEOUT = 30


class Logging(object):

	""" Settings for logger (console -and file-handler) """

	TO_CONSOLE 		= True
	TO_FILE 		= True
	UNIQUE_FILENAME = False

	LOGLEVEL_CONSOLE = logging.DEBUG
	LOGLEVEL_FILE 	 = logging.DEBUG


class TCPIP(object):

	""" Settings for TCP/IP-layer """

	TIME_INTERVAL_PING 	= 3
	TIME_RECONNECT 		= 15
	ALIVE_TIMEOUT 		= 10
	MAX_ATTEMPTS 		= 5


class SignalDB(object):

	""" XML signal-db """

	PATH = os.path.join("resources", "data", "signal-db", "SignalDatabase.xml")


class Events(object):

	"""
	different settings for events, etc..
	"""

	SCROLL_SPEED = 0.05
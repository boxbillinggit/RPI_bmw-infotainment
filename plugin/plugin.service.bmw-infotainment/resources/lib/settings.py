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


class System(object):

	"""	System settings	"""

	# shutdown after 30min idle (after key has been pulled out from ignition lock)
	IDLE_SHUTDOWN = 30 * 60


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
	MAX_ATTEMPTS 		= 10

	LOG_BUS_ACTIVITY = False

class SignalDB(object):

	""" XML signal-db """

	PATH = os.path.join("resources", "data", "signal-db", "SignalDatabase.xml")


class Buttons(object):

	"""	Settings for BUTTONS, etc..	"""

	STATE_HOLD_INIT 	= 1.5
	STATE_HOLD_INTERVAL = 0.5
	STATE_HOLD_N_MAX	= 5 	# default number of times max allowed
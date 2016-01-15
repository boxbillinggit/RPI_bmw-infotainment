"""
This logger module handles both logging to file and console. If we are running
service from XBMC/KODI (normal case) we forward console log-messages to KODI/XBMC
log-module. If we running service command-line the console is used as output.

Enable DEBUG-log for XBMC/KODI:
	* Navigate to "settings -> system -> debugging"
	* Logfile is found under "~/.kodi/temp"

References:
https://docs.python.org/3/howto/logging.html
http://kodi.wiki/view/Log_file/Advanced#Enable_debugging
"""

import logging
import os
import datetime

try:
	import xbmc, xbmcgui, xbmcaddon
	USING_XBMC = True

except ImportError as err:
	import debug.xbmc as xbmc
	import debug.xbmcgui as xbmcgui
	import debug.xbmcaddon as xbmcaddon
	USING_XBMC = False

# import local modules
import settings

__author__ 		= 'Lars'
__addon__		= xbmcaddon.Addon()
__addonid__		= __addon__.getAddonInfo('id')
__addonpath__	= __addon__.getAddonInfo('path')


# XBMC/KODI Debug levels
LOGDEBUG 	= 0
LOGINFO 	= 1
LOGNOTICE 	= 2
LOGWARNING 	= 3
LOGERROR 	= 4
LOGSEVERE 	= 5
LOGFATAL 	= 6
LOGNONE 	= 7


FNAME_UNIQUE = "{}-{}.log".format(__addonid__, datetime.datetime.now().strftime("%Y-%m-%d-%H%M%S"))
FNAME = "{}.log".format(__addonid__)

LOGPATH = os.path.join(xbmc.translatePath("special://logpath"), FNAME_UNIQUE if settings.Logging.UNIQUE_FILENAME else FNAME)


class LogHandler(object):

	"""
	Setup handlers for console -and file
	"""

	# ref: https://docs.python.org/3/library/logging.html?highlight=logger#logging.Formatter
	formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(name)s - %(message)s')

	def __init__(self, formatter):

		self.fh = None
		self.ch = None
		self.formatter = formatter

		if settings.Logging.TO_FILE:
			self.init_file_handle()

		# KODI/XBMC has no console - use 'xbmc.log' instead
		if settings.Logging.TO_CONSOLE and USING_XBMC:
			self.init_console_xbmc()
		elif settings.Logging.LOGLEVEL_CONSOLE and not USING_XBMC:
			self.init_console_stdout()

	def init_file_handle(self):

		fh = logging.FileHandler(LOGPATH, mode="w")
		fh.setLevel(settings.Logging.LOGLEVEL_FILE)
		fh.setFormatter(self.formatter)
		self.fh = fh

	def init_console_xbmc(self):

		# add special XBMC handler
		ch = XBMCLogger()
		ch.setLevel(settings.Logging.LOGLEVEL_CONSOLE)
		self.ch = ch

	def init_console_stdout(self):

		ch = logging.StreamHandler()
		ch.setLevel(settings.Logging.LOGLEVEL_CONSOLE)
		ch.setFormatter(self.formatter)
		self.ch = ch


class XBMCLogger(logging.Handler):

	"""
	No monitor when running XBMC/KODI - forward messages to XBMC/KODI-log
	instead.
	"""

	def __init__(self):

		self.xbmc_loglevel = {
			"DEBUG": LOGDEBUG,
			"INFO": LOGINFO,
			"WARNING": LOGWARNING,
			"ERROR": LOGERROR,
			"CRITICAL": LOGFATAL
			}

		logging.Handler.__init__(self)

	def emit(self, record):

		msg = "%s: %s" % (__addonid__, record.msg)

		# map XBMC-loglevel against built-in loglevels (default level is 'LOGINFO')
		level = self.xbmc_loglevel.get(record.levelname, LOGINFO)

		xbmc.log(msg, level)


log_handler = LogHandler(LogHandler.formatter)


def hexstring(data):

	"""
	Print a well formed HEX-string from type "bytearray"
	"""

	return " ".join(map(lambda byte: "%X" % byte, data)) if data else ""


def pritty_hex(data):

	"""
	print a pretty HEX-string by removing "0x" and capitalize letters.
	"""

	return " ".join(data).replace("0x", "").upper()


def init_logger(name, log_level=None):

	"""
	Main function for creating a new logger module.
	"""

	# instantiate a new logger
	logger = logging.getLogger(name)

	# no log-level was provided, set to lowest level (capture all)
	if not log_level:
		logger.setLevel(min(settings.Logging.LOGLEVEL_CONSOLE, settings.Logging.LOGLEVEL_FILE))

	if log_handler.ch:
		logger.addHandler(log_handler.ch)

	if log_handler.fh:
		logger.addHandler(log_handler.fh)

	return logger

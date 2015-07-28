# TODO: rename to "DebugHandler.py" -or "LogDebug.py"?
"""
Debug logger handles both XBMC-lgging -and console logging.

References:
Python logging - https://docs.python.org/3/howto/logging.html
XBMC/KODI logging - http://kodi.wiki/view/Log_file/Advanced#Enable_debugging

Enable DEBUG-log for kodi:
* enter "settings -> system -> debugging"
* logfile is found under "%APPDATA%\AppData\Roaming\Kodi"
"""

try:
	import xbmc, xbmcplugin, xbmcgui, xbmcaddon
	USING_XBMC = True

except ImportError as err:
	import debug.XBMC as xbmc
	import debug.XBMCGUI as xbmcgui
	import debug.XBMCADDON as xbmcaddon
	USING_XBMC = False

__author__ 		= 'Lars'
__addon__		= xbmcaddon.Addon()
__addonid__		= __addon__.getAddonInfo('id')

import settings, logging
import os, sys

# XBMC/KODI Debug levels
LOGDEBUG 	= 0
LOGINFO 	= 1
LOGNOTICE 	= 2
LOGWARNING 	= 3
LOGERROR 	= 4
LOGSEVERE 	= 5
LOGFATAL 	= 6
LOGNONE 	= 7

LOGPATH = os.path.join(os.getcwd(), settings.LOGFILE)

def init_logger(name):

	log = logging.getLogger(name)

	# set overall logging level (the lowest level)
	log.setLevel(min(settings.LOGLEVEL_CONSOLE, settings.LOGLEVEL_FILE))

	# https://docs.python.org/3/library/logging.html?highlight=logger#logging.Formatter
	formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')

	# log to file
	if settings.LOG_TO_FILE:

		# TODO: this must be possible to have common for each logger
		fh = logging.FileHandler(LOGPATH)
		fh.setLevel(settings.LOGLEVEL_FILE)
		fh.setFormatter(formatter)
		log.addHandler(fh)

	# KODI/XBMC has no console - use 'xbmc.log' instead
	if settings.LOG_TO_CONSOLE and USING_XBMC:

		# add special XBMC handler
		xbmc_log = XBMCLogger()
		xbmc_log.setLevel(settings.LOGLEVEL_CONSOLE)
		log.addHandler(xbmc_log)


	# log to console
	elif settings.LOGLEVEL_CONSOLE and not USING_XBMC:
		ch = logging.StreamHandler()
		ch.setLevel(settings.LOGLEVEL_CONSOLE)
		ch.setFormatter(formatter)
		log.addHandler(ch)

	return log

class Logger(object):

	def __init__(self):

		pass


class XBMCLogger(logging.Handler):

	"""
	We don't have a monitor when running XBMC/KODI - pipe messages to XBMC-log
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

		# init base class
		logging.Handler.__init__(self)

	def emit(self, record):

		# format log mesage
		msg = "%s: %s" % (__addonid__, record.msg)

		# map XBMC-loglevel against built-in loglevels (default level is 'LOGINFO')
		level = self.xbmc_loglevel.get(record.levelname, LOGINFO)

		# log to XBMC
		xbmc.log(msg, level)

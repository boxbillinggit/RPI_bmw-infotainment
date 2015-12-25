"""
Debug logger handles both XBMC-lgging -and console logging. If we're
using XBMC- we pipe console-messages to 'xbmc.log' instead

References:
Python logging - https://docs.python.org/3/howto/logging.html
XBMC/KODI logging - http://kodi.wiki/view/Log_file/Advanced#Enable_debugging

Enable DEBUG-log for kodi:
* enter "settings -> system -> debugging"
* logfile is found under "~/.kodi/temp"
"""

try:
	import xbmc, xbmcplugin, xbmcgui, xbmcaddon
	USING_XBMC = True

except ImportError as err:
	import debug.xbmc as xbmc
	import debug.xbmcgui as xbmcgui
	import debug.xbmcaddon as xbmcaddon
	USING_XBMC = False

__author__ 		= 'Lars'
__addon__		= xbmcaddon.Addon()
__addonid__		= __addon__.getAddonInfo('id')
__addonpath__	= __addon__.getAddonInfo('path')

import settings, logging
import os, datetime

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

LOGPATH = os.path.join(xbmc.translatePath("special://logpath"), FNAME_UNIQUE if settings.LOG_FILENAME_UNIQUE else FNAME)

# ref: https://docs.python.org/3/library/logging.html?highlight=logger#logging.Formatter
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')


class Handles(object):

	"""
	Setup handles for console -and file
	"""

	def __init__(self, formatter):

		self.fh = None
		self.ch = None
		self.formatter = formatter

		# init handles
		if settings.LOG_TO_FILE:
			self.init_file_handle()

		# KODI/XBMC has no console - use 'xbmc.log' instead
		if settings.LOG_TO_CONSOLE and USING_XBMC:
			self.init_console_xbmc()
		elif settings.LOGLEVEL_CONSOLE and not USING_XBMC:
			self.init_console_stdout()

	def init_file_handle(self):

		fh = logging.FileHandler(LOGPATH, mode="w")
		fh.setLevel(settings.LOGLEVEL_FILE)
		fh.setFormatter(self.formatter)
		self.fh = fh

	def init_console_xbmc(self):

		# add special XBMC handler
		ch = XBMCLogger()
		ch.setLevel(settings.LOGLEVEL_CONSOLE)
		self.ch = ch

	def init_console_stdout(self):

		ch = logging.StreamHandler()
		ch.setLevel(settings.LOGLEVEL_CONSOLE)
		ch.setFormatter(self.formatter)
		self.ch = ch


class XBMCLogger(logging.Handler):

	"""
	No monitor when running XBMC/KODI - pipe messages to XBMC-log
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


# init handles
handles = Handles(formatter)


def init_logger(name, log_level=None):

	# instantiate module's logger
	log = logging.getLogger(name)

	# no loglevel was passed, set to lowest level (capture all)
	if not log_level:
		log.setLevel(min(settings.LOGLEVEL_CONSOLE, settings.LOGLEVEL_FILE))

	if handles.ch:
		log.addHandler(handles.ch)

	if handles.fh:
		log.addHandler(handles.fh)

	return log

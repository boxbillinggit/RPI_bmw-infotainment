__author__ = 'Lars'

import signal, sys, time
from threading import Thread

# fixes the log-problem, for using functions within IDE (PyCharm)

LOGDEBUG = 0
LOGERROR = 4
LOGFATAL = 6
LOGINFO = 1
LOGNONE = 7
LOGNOTICE = 2
LOGSEVERE = 5
LOGWARNING = 3

# TODO implement using logging class, not print.
def log(arg, level):
	print "%s (loglevel: %s)" % (arg, level)


def executebuiltin(arg):
	print("%s - Execute in XBMC/KODI: %s" % (__name__, arg))


def exit_main_thread(sig, frame):
	print "%s - Bye!" % __name__
	sys.exit(0)


def main_thread():

	signal.signal(signal.SIGINT, exit_main_thread)

	while (True):
		time.sleep(30)


# Wrapper when running script from IDE
class Monitor(object):

	def __init__(self):
		pass

	def abortRequested(self):
		return False

	def waitForAbort(self):

		main_thread()

		# TODO: will never be executed, no clean shutdown...
		return True

# enable DEBUG-log for kodi:
# http://kodi.wiki/view/Log_file/Advanced#Enable_debugging
# enter "settings -> system -> debugging"
# logfile is under "C:\Users\Lars\AppData\Roaming\Kodi"
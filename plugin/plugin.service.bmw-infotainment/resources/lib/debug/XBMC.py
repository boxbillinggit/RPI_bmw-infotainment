__author__ = 'Lars'

import signal, sys, time

LOGLEVELS={
	0: "LOGDEBUG",
	1: "LOGINFO",
	2: "LOGNOTICE",
	3: "LOGWARNING",
	4: "LOGERROR",
	5: "LOGSEVERE",
	6: "LOGFATAL",
	7: "LOGNONE"
}


# DEBUG - just for testing the 'log.py'-module
def log(arg, level):
	print("%s - %s" % (LOGLEVELS.get(level, 'UNKNOWN'), arg))


def executebuiltin(arg):
	print("%s - Execute in XBMC/KODI: %s" % (__name__, arg))


def _exit_main_thread(sig, frame):
	print("%s - Bye!" % __name__)
	sys.exit(0)


def main_thread():

	signal.signal(signal.SIGINT, _exit_main_thread)

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

__author__ = 		'Lars'
__modulename__ = 	"xbmc"

import signal, time

import events

# can be overriden from test-script
event = events.Debug()

LOGLEVELS = {
	0: "LOGDEBUG",
	1: "LOGINFO",
	2: "LOGNOTICE",
	3: "LOGWARNING",
	4: "LOGERROR",
	5: "LOGSEVERE",
	6: "LOGFATAL",
	7: "LOGNONE"
}

# ref: http://kodi.wiki/view/Special_protocol
specialpaths = {
	"special://logpath": 	"~/.kodi/temp",
	"special://home": 		"~/.kodi/",
	"special://skin": 		"~/.kodi/addons"
}


# DEBUG - just for testing the 'log.py'-module
def log(arg, level):
	print("%s - %s" % (LOGLEVELS.get(level, 'UNKNOWN'), arg))


def executebuiltin(arg):
	event.emit(module=__modulename__, method="executebuiltin", args=arg)


def translatePath(path):
	return specialpaths.get(path)


def exit_main_thread(sig, frame):
	Monitor.abort_requested = True


def main_thread():

	signal.signal(signal.SIGINT, exit_main_thread)

	while not Monitor.abort_requested:
		time.sleep(1)


# Wrapper when running script from IDE
class Monitor(object):

	abort_requested = False

	def __init__(self):
		pass

	def abortRequested(self):
		return Monitor.abort_requested

	def waitForAbort(self):

		main_thread()

		return True
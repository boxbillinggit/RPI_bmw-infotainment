__author__ = 'Lars'

# fixes the log-problem, for using functions within IDE (PyCharm)

# Wrapper when running script from IDE
class XBMC(object):

	LOGDEBUG = 0
	LOGERROR = 4
	LOGFATAL = 6
	LOGINFO = 1
	LOGNONE = 7
	LOGNOTICE = 2
	LOGSEVERE = 5
	LOGWARNING = 3

	def __init__(self):
		pass

	# TODO implement using logging class, not print.
	def log(self, arg, loglevel):
		print "%s (loglevel: %s)" % (arg, loglevel)

	def executebuiltin(self, arg):
		print("Execute in XBMC/KODI: %s" % arg)

# enable DEBUG-log for kodi:
# http://kodi.wiki/view/Log_file/Advanced#Enable_debugging
# enter "settings -> system -> debugging"
# logfile is under "C:\Users\Lars\AppData\Roaming\Kodi"
__author__ = 'Lars'

import time


# special for test-scripts to catch events executed in XBMC/KODI. This will be overriden
# from test-script. so without test-script just print to console.
def emit(src="unknown", args=None):
	print("{}: {}".format(src, args))


class Dialog(object):

	def __init__(self):
		pass

	def yesno(self, *arg):

		# prevents the prompt to be disturbed from log message
		time.sleep(0.5)
		return False if "n" == raw_input(". ".join(arg)+"(y/n) [y] >> ") else True

	def notification(self, *arg):
		emit(src="{}.{}.notification".format(__name__, self.__class__.__name__), args=". ".join(arg))


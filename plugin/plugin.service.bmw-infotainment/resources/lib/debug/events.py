__author__ = 'lars'


class Debug(object):

	"""
	Special class for handling events in XBMC/KODI during debugging. Events and user-inputs
	will be handled from console if starting service.py from command-line. If using with
	test-script, this class will be overriden.
	"""

	def emit(self, src="unknown", args=None):
		print("{}: \"{}\"".format(src, args))

	def user_input(self, src="unknown", args=None, default="unknown"):
		print src
		return raw_input("{}: [{}] >>".format(args, default))

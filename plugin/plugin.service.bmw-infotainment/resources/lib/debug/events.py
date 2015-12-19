__author__ = 'lars'


class Debug(object):

	"""
	Special class for handling events in XBMC/KODI during debugging. Events and user-inputs
	will be handled from console if starting service.py from command-line. If using with
	test-script, this class will be overriden.
	"""

	def emit(self, module="", method="", args=None):
		print("{} - {}: \"{}\"".format(module, method, args))

	def user_input(self, module="", method="", args=None, default=""):
		print "{} - {}".format(module, method)
		return raw_input("{}: [{}] >>".format(args, default))

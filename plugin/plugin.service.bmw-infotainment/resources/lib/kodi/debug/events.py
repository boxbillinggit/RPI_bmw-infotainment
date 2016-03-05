import datetime
__author__ = 'lars'

USE_DEFAULT = True


class Debug(object):

	"""
	Special class for handling events in XBMC/KODI during debugging. Events and user-inputs
	will be handled from console if starting service.py from command-line. If using with
	test-script, this class will be overriden.
	"""

	def emit(self, module="", method="", args=None):
		now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S,%f")
		print("{} - {} - {}: \"{}\"".format(now, module, method, args))

	def user_input(self, module="", method="", args=None, default=""):
		print "{} - {}".format(module, method)

		if USE_DEFAULT:
			print ("{} >> {}".format(args, default))
			return default

		return raw_input("{}: [{}] >>".format(args, default))

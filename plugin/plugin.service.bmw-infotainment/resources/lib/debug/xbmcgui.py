__author__ = 'Lars'

import time
import events

# can be overriden from test-script
event = events.Debug()


class Dialog(object):

	def __init__(self):
		pass

	def yesno(self, *arg):

		# sleep prevents the prompt to be disturbed from log message
		time.sleep(0.5)
		response = event.user_input(src="{}.{}.notification".format(__name__, self.__class__.__name__), args=("\n".join(arg)+" (y/n)"), default="y")

		return False if "n" == response else True

	def notification(self, *arg):
		event.emit(src="{}.{}.notification".format(__name__, self.__class__.__name__), args=". ".join(arg))


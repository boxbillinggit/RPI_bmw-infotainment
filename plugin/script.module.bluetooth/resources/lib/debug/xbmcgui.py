__author__ = 'Lars'

import time

class Dialog(object):

	def __init__(self):
		pass

	def yesno(self, *arg):

		# prevents the prompt to be disturbed from log message
		time.sleep(0.5)
		return "y" == raw_input(". ".join(arg)+"(y/n) >> ")

	def notification(self, *arg):
		print("%s - Notification: %s " % (__name__, (". ".join(arg))))

class WindowXML(object):

	def __init__(self):
		pass
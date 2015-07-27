__author__ = 'Lars'


class Dialog(object):

	def __init__(self):
		pass

	def yesno(self, *arg):
		return "y" == raw_input(". ".join(arg))

	def notification(self, *arg):
		print "%s - Notification dialog: %s " % (__name__, (". ".join(arg)))
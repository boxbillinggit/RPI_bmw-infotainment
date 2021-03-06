__author__ = 		'Lars'
__modulename__ = 	"xbmcgui"

import time
import events

# can be overriden from test-script
event = events.Debug()


class Window(object):

	def __init__(self, *args, **kwargs):
		pass

	def doModal(self):
		pass

	def close(self):
		pass

	@classmethod
	def getControl(cls, control_id):
		return Control()


class WindowXML(Window):
	pass


class WindowXMLDialog(Window):
	pass


class Control(object):

	def setLabel(self):
		pass


class Dialog(object):

	def __init__(self):
		pass

	def yesno(self, *arg):

		# sleep prevents the prompt to be disturbed from log message
		time.sleep(0.5)
		response = event.user_input(module=__modulename__, method="%s.yesno" % self.__class__.__name__, args=("\n".join(arg)+" (y/n)"), default="y")

		return False if "n" == response else True

	def notification(self, *arg):
		event.emit(module=__modulename__, method="%s.notification" % self.__class__.__name__, args=". ".join(arg))


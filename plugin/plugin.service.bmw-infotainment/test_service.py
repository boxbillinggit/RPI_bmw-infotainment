"""
This module is used to test service.py from command-line.

Start:
>> import tests.test_service as testmodule
>> testmodule.gateway.start()
>> testmodule.service.start()

Send:
>> testmodule.send(("IBUS_DEV_BMBT", "IBUS_DEV_RAD", "right-knob.release"))

Stop:
>> testmodule.service.stop()
>> testmodule.gateway.stop()
"""

import datetime

# import local modules
import service as module_service
import tests.gateway as module_gateway
import resources.lib.signaldb as signaldb

__author__ = 'lars'


class Events(object):

	"""
	The emulated interface against XBMC/KODI

	Special class for handling events in XBMC/KODI during debugging. Events and user-inputs
	will now be controlled by the test script - instead of using the console as interface.
	This overrides the class in 'events.py'.
	"""

	def emit(self, module="", method="", args=None):
		now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S,%f")
		print("{} - {} - {}: \"{}\"".format(now, module, method, args))

	def user_input(self, module="", method="", args=None, default=""):
		print "{}: {} - {}".format(__name__, module, method)
		print ">> %s (answering default)" % default
		return default


# rebind callbacks from XBMC/KODI.
# testmodule.__name__ == testmodule.module_service.xbmc.event.__module__
event = Events()
module_service.xbmc.event = event
module_service.xbmcgui.event = event
module_service.xbmcaddon.event = event

# shortcuts
gateway = module_gateway.Gateway()
service = module_service.TCPIPHandler()


def send(msg):

	"""
	Send message from description.

	example: send(("IBUS_DEV_BMBT", "IBUS_DEV_RAD", "right-knob.release"))
	"""

	module_gateway.broadcast(signaldb.find(msg))


def send_raw(msg):

	"""
	Send raw message in bytes.

	example: send_raw(([src], [dst], [data]))
	"""

	module_gateway.broadcast(bytearray(msg))


if __name__ == "__main__":
	pass

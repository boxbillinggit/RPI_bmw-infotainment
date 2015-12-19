__author__ = 'lars'

import os, sys

# fix path resolution for module import
rootpath = os.path.normpath(os.path.join(os.getcwd(), "../"))
sys.path.append(rootpath)

import service as module_service
import gateway as module_gateway


# the interface against XBMC/KODI
class Debug(object):

	"""
	Special class for handling events in XBMC/KODI during debugging. Events and user-inputs
	will now be controlled by the test script - instead of using the console as interface.
	This overrides the class in 'events.py'.
	"""

	def emit(self, src="unknown", args=None):
		print("from testscript - {}: \"{}\"".format(src, args))

	def user_input(self, src="unknown", args=None, default="unknown"):
		print "from testscript - %s" % src
		return raw_input("{}: [{}] >>".format(args, default))


# shortcuts
# NOTE - this will start the gateway when importing.
gateway = module_gateway.Gateway()
service = module_service.service

# XBMC/KODI event interface
event = Debug()

# bind callbacks to XBMC/KODI debug-interface
# verify binding by calling command-line: testmodule.module_service.xbmc.event.__module__
module_service.xbmc.event = event
module_service.xbmcgui.event = event
module_service.xbmcaddon.event = event


# start plugin from command-line:
#
# import tests.test_service as testmodule
# testmodule.service.start()
#


def start():

	# start service
	service.start()

	if module_service.__monitor__.waitForAbort():
		service.stop()


if __name__ == "__main__":

	start()
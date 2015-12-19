__author__ = 'lars'

import os, sys
import threading

# fix path resolution for module import
rootpath = os.path.normpath(os.path.join(os.getcwd(), "../"))
sys.path.append(rootpath)

import service as srv
import gateway as testsrv

# set emit callbacks
def emit(src="unknown", args=None):
	print("from test-script - {}: {}".format(src, args))


srv.xbmc.emit = emit
srv.xbmcgui.emit = emit
srv.xbmcaddon.emit = emit

# verify binding by calling:
# tst.srv.xbmc.emit.__module__

# start from command-line:
#
# import tests.test_service as tst
# tst.srv.service.start()
#
# or
#
# tst.start()


def start():

	# start service
	srv.service.start()

	if srv.__monitor__.waitForAbort():
		srv.service.stop()



if __name__ == "__main__":

	start()
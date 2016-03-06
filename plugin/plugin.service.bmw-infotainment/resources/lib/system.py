import time
import log as log_module
import settings
import signaldb
import event_handler

import kodi.builtin

log = log_module.init_logger(__name__)
__author__ = 'lars'


class SystemState(object):

	""" Storage class for system states """

	request_shutdown = False


def init_events(bind_event):

	""" system shutdown, GPIO-pins, etc..  """

	bind_event(signaldb.create(("IBUS_DEV_EWS", "IBUS_DEV_GLO", "ign-key.in")), abort_shutdown)
	bind_event(signaldb.create(("IBUS_DEV_EWS", "IBUS_DEV_GLO", "ign-key.out")), schedule_shutdown)


def screen_on():

	""" Turn on GPIO pin #X to activate RCA input """

	pass


def screen_off():

	""" turn off GPIO pin #X and deactivate RCA input """

	pass


def schedule_shutdown():

	""" Schedule shutdown only once """

	if not SystemState.request_shutdown:

		shutdown_time = settings.System.IDLE_SHUTDOWN

		event_handler.add(kodi.builtin.shutdown, timestamp=time.time()+shutdown_time)
		log.info("System shutdown is scheduled within {} min".format(shutdown_time/60))

	SystemState.request_shutdown = True


def abort_shutdown():

	""" Driver came back within time, abort shutdown """

	if SystemState.request_shutdown:
		event_handler.remove(kodi.builtin.shutdown)
		log.info("Welcome back! (Aborting system shutdown request)")

	SystemState.request_shutdown = False

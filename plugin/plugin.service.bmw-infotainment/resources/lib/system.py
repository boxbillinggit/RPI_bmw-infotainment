import time
import log as log_module
import signaldb
import event_handler
import kodi.builtin
import kodi.addon_settings

log = log_module.init_logger(__name__)
__author__ = 'lars'

# TODO: notify when shutdown is scheduled (won't be visible anyway, but during testing/debugging)


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

	shutdown = kodi.addon_settings.schedule_shutdown()

	if (shutdown is not None) and (not SystemState.request_shutdown):

		event_handler.add(kodi.builtin.shutdown, timestamp=time.time()+shutdown)
		log.info("System shutdown is scheduled within {} min".format(shutdown/60))

	SystemState.request_shutdown = True


def abort_shutdown():

	""" Driver came back within time, abort shutdown """

	if SystemState.request_shutdown:
		event_handler.remove(kodi.builtin.shutdown)
		log.info("Welcome back! (Aborting system shutdown request)")

	SystemState.request_shutdown = False

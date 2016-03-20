import time
import log as log_module
import signaldb
import event_handler
from kodi import __xbmcgui__, __addonid__
import kodi.builtin
import kodi.addon_settings

log = log_module.init_logger(__name__)
__author__ = 'lars'


class SystemState(object):

	""" Storage class for system states """

	request_shutdown = False


def init_events(bind_event):

	""" system shutdown, GPIO-pins, etc..  """

	# TODO: ignition in is not detected (no bus-signal exists accordingly to signal-db)
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

		msg = "System shutdown in {} min".format(shutdown/60)
		log.info(msg)

		__xbmcgui__.Dialog().notification(__addonid__, msg)

	SystemState.request_shutdown = True


def abort_shutdown():

	""" Driver came back within time, abort shutdown """

	if SystemState.request_shutdown:
		event_handler.remove(kodi.builtin.shutdown)
		log.info("Welcome back! (Aborting system shutdown request)")

	SystemState.request_shutdown = False

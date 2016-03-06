"""
For debugging, record signals to log
"""

import signaldb
import log as log_module

log = log_module.init_logger(__name__)

__author__ = 'lars'


def init_events(bind_event):

	""" bind some analyzing events """

	# catch arbitrary data from radio to graphics driver (forward data to method)
	# bind_event(signaldb.create(("IBUS_DEV_RAD", "IBUS_DEV_GT", "ARBITRARY"), DATA="(.*)"), debug_monitor, "RAD -> GT: ")
	# bind_event(signaldb.create(("IBUS_DEV_GT", "IBUS_DEV_RAD", "ARBITRARY"), DATA="(.*)"), debug_monitor, "GT -> RAD: ")

	src, dst = "IBUS_DEV_BMBT", "IBUS_DEV_RAD"

	# catch mode-changing button events
	bind_event(signaldb.create((src, dst, "mode.push")), log.debug, "mode.push")
	bind_event(signaldb.create((src, dst, "menu.push")), log.debug, "menu.push")
	bind_event(signaldb.create((src, dst, "AM.push")), log.debug, 	"AM.push")
	bind_event(signaldb.create((src, dst, "FM.push")), log.debug, 	"FM.push")
	bind_event(signaldb.create((src, dst, "tone.push")), log.debug, "tone.push")
	bind_event(signaldb.create((src, dst, "source.push")), log.debug, "source.push")

	# F0 05 FF 47 00 0F 42 -> select push (to GLOBAL)
	# F0 05 FF 47 00 38 75 -> info push
	# F0 04 FF 48 87 C4 -> clock.push
	bind_event(signaldb.create((src, None, "select.push")), log.debug, "select.push")
	bind_event(signaldb.create((src, None, "info.push")), log.debug, 	"info.push")
	bind_event(signaldb.create((src, None, "clock.push")), log.debug, 	"clock.push")


def debug_monitor(heading, data):

	log.debug(heading + data.replace("0x", "").upper())

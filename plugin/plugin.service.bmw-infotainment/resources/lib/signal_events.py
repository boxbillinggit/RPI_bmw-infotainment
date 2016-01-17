"""
Handle initialization of all events, also implements methods for adding
and removing events at runtime.
"""

import kodi
import signaldb
import system as module_system
from signal_methods import hexstring
from buttons import Button

import log as log_module
log = log_module.init_logger(__name__)

__author__ = 'lars'


class Index(object):

	"""
	Unique index for each event added on event-stack.
	"""

	def __init__(self):
		self.index = 0

	def inc(self):
		self.index += 1
		return self.index


def init_system_events(bind_event):

	"""
	State-machine for controlling power off and current MID-state (CD, TAPE, RADIO, etc..)
	"""

	system = module_system.State()
	bind_event(signaldb.create(("IBUS_DEV_EWS", "IBUS_DEV_GLO", "ign-key.in")), system.set_state_init)
	bind_event(signaldb.create(("IBUS_DEV_EWS", "IBUS_DEV_GLO", "ign-key.out")), system.set_state_shutdown)

	# identifiers for currrent MID-state
	# TODO: not fully implemented (need regexp to match data after (end of string), etc..)
	bind_event(signaldb.create((None, "IBUS_DEV_GT", "text-area.unknown"), DATA=hexstring("CDC")), None)
	bind_event(signaldb.create((None, "IBUS_DEV_GT", "text-area.unknown"), DATA=hexstring("TAPE")), None)

	# a state change is about to happen TODO get source and dst
	mode_btn = Button(release=system.button_pressed)
	bind_event(signaldb.create((None, None, "mode.push")), mode_btn.set_state_push)
	bind_event(signaldb.create((None, None, "mode.release")), mode_btn.set_state_release)


def init_controls(bind_event):

	"""
	Initialize all events for buttons.
	"""

	src, dst = ("IBUS_DEV_BMBT", None)

	# regular expression for scroll speed (forwarded to method)
	regexp = "([1-9])"

	right_knob = Button(hold=kodi.action("back"), release=kodi.action("Select"))
	bind_event(signaldb.create((src, dst, "right-knob.push")), right_knob.set_state_push)
	bind_event(signaldb.create((src, dst, "right-knob.hold")), right_knob.set_state_hold)
	bind_event(signaldb.create((src, dst, "right-knob.release")), right_knob.set_state_release)
	bind_event(signaldb.create((src, dst, "right-knob.turn-left"), SCROLL_SPEED=regexp), kodi.action("up"))
	bind_event(signaldb.create((src, dst, "right-knob.turn-right"), SCROLL_SPEED=regexp), kodi.action("down"))

	left = Button(hold=kodi.action("Left"), release=kodi.action("Left"))
	bind_event(signaldb.create((src, dst, "left.push")), left.set_state_push)
	bind_event(signaldb.create((src, dst, "left.hold")), left.set_state_hold)
	bind_event(signaldb.create((src, dst, "left.release")), left.set_state_release)

	right = Button(hold=kodi.action("Right"), release=kodi.action("Right"))
	bind_event(signaldb.create((src, dst, "right.push")), right.set_state_push)
	bind_event(signaldb.create((src, dst, "right.hold")), right.set_state_hold)
	bind_event(signaldb.create((src, dst, "right.release")), right.set_state_release)


class Events(object):

	"""
	Main Class for this module. Initializes default events. it is also possible
	to dynamically update, add -or remove events at runtime.
	"""

	INDEX, SIGNAL, METHOD, ARGS, KWARGS = range(5)

	def __init__(self):

		self.list = []
		self.index = Index()

		init_controls(self.bind_event)
		init_system_events(self.bind_event)

	def bind_event(self, signal, method, *args, **kwargs):

		"""
		Add one event to list. if keyword argument "static=False" is used, event will
		be deleted from list after execution (one-time event)
		"""

		index = self.index.inc()
		item = (index, signal, method, args, kwargs)

		self.list.append(item)
		return index

	def unbind_event(self, ref):

		"""
		Remove one event, with index as reference.
		"""

		for item in self.list:

			index = item[Events.INDEX]

			if index == ref:
				self.list.remove(item)
				return index

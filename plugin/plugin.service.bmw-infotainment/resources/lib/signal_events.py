"""
Handle initialization of all events, also implements methods for adding
and removing events at runtime.
"""

import time

# import local modules
import kodi
import signaldb
from buttons import Button, State

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


# TODO: fix statemachine for power-on power-off, CD-emulation DISABLED-ENABLED, etc...
def init_statemachine(bind_event):
	pass


def init_buttons(button, bind_event):

	"""
	Initialize all events for buttons.
	"""

	src, dst = ("IBUS_DEV_BMBT", None)

	# regular expression for scroll speed (this data is matched and forwarded to method)
	regexp = "([1-9])"

	right_knob = button.new(hold=kodi.action("back"), release=kodi.action("Select"))
	bind_event(signaldb.create((src, dst, "right-knob.push")), right_knob.set_state_push)
	bind_event(signaldb.create((src, dst, "right-knob.hold")), right_knob.set_state_hold)
	bind_event(signaldb.create((src, dst, "right-knob.release")), right_knob.set_state_release)
	bind_event(signaldb.create((src, dst, "right-knob.turn-left"), SCROLL_SPEED=regexp), kodi.action("up"))
	bind_event(signaldb.create((src, dst, "right-knob.turn-right"), SCROLL_SPEED=regexp), kodi.action("down"))

	left = button.new(hold=kodi.action("Left"), release=kodi.action("Left"))
	bind_event(signaldb.create((src, dst, "left.push")), left.set_state_push)
	bind_event(signaldb.create((src, dst, "left.hold")), left.set_state_hold)
	bind_event(signaldb.create((src, dst, "left.release")), left.set_state_release)

	right = button.new(hold=kodi.action("Right"), release=kodi.action("Right"))
	bind_event(signaldb.create((src, dst, "right.push")), right.set_state_push)
	bind_event(signaldb.create((src, dst, "right.hold")), right.set_state_hold)
	bind_event(signaldb.create((src, dst, "right.release")), right.set_state_release)


class ButtonFactory(object):

	"""
	Factory class for creating new instances of "NewButton".
	"""

	def __init__(self, scheduler):
		self.scheduler = scheduler

	def new(self, **kwargs):
		return NewButton(self.scheduler, **kwargs)


class NewButton(Button):

	"""
	Used to create a new button. This class implements a method for
	"schedule_check_state_hold" (not implemented in Base class).
	"""

	def __init__(self, scheduler, **kwargs):
		super(NewButton, self).__init__(**kwargs)
		self.scheduler = scheduler

	def schedule_check_state_hold(self, timeout=State.HOLD_INIT):
		# log.debug("{} -schedule_check_state_hold() ".format(self.__class__.__name__))
		self.scheduler.add(self.check_state_hold, timestamp=timeout+time.time())


class Events(object):

	"""
	Main Class for this module. Initializes default events. it is also possible
	to dynamically update, add -or remove events at runtime.
	"""

	def __init__(self, scheduler):

		self.list = []
		self.scheduler = scheduler
		self.index = Index()

		# add events
		init_buttons(ButtonFactory(self.scheduler), self.bind_event)
		init_statemachine(self.bind_event)

	def bind_event(self, signal, method, **kwargs):

		"""
		Add one event to list. if keyword argument "static=False" is used, event will
		be deleted from list after execution (one-time event)
		"""
		
		index = self.index.inc()
		item = (index, signal, method, kwargs)

		self.list.append(item)
		return index

	def unbind_event(self, ref):

		"""
		Remove one event, with index as reference.
		"""
		
		for item in self.list:
			
			index, signal, method, kwargs = item
		
			if index == ref:
				self.list.remove(item)
				return index

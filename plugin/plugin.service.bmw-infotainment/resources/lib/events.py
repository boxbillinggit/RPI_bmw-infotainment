"""
Handle initialization of all events, and also adding, or removing events.
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

	def __init__(self):
		self.index = 0

	def inc(self):
		self.index += 1
		return self.index


def init_buttons(factory=None, index=None):

	"""
	Initialize all events for buttons.
	"""

	events = []
	button = factory
	SRC, DST = ("IBUS_DEV_BMBT", None)

	right_knob = button.new(hold=kodi.action("back"), release=kodi.action("enter"))
	events.append((index(), signaldb.create((SRC, DST, "right-knob.push")), right_knob.set_state_push))
	events.append((index(), signaldb.create((SRC, DST, "right-knob.hold")), right_knob.set_state_hold))
	events.append((index(), signaldb.create((SRC, DST, "right-knob.release")), right_knob.set_state_release))
	events.append((index(), signaldb.create((SRC, DST, "right-knob.turn-left")), kodi.action("up")))
	events.append((index(), signaldb.create((SRC, DST, "right-knob.turn-right")), kodi.action("down")))

	left = button.new(hold=kodi.action("Left"), release=kodi.action("Left"))
	events.append((index(), signaldb.create((SRC, DST, "left.push")), left.set_state_push))
	events.append((index(), signaldb.create((SRC, DST, "left.hold")), left.set_state_hold))
	events.append((index(), signaldb.create((SRC, DST, "left.release")), left.set_state_release))

	right = button.new(hold=kodi.action("Right"), release=kodi.action("Right"))
	events.append((index(), signaldb.create((SRC, DST, "right.push")), right.set_state_push))
	events.append((index(), signaldb.create((SRC, DST, "right.hold")), right.set_state_hold))
	events.append((index(), signaldb.create((SRC, DST, "right.release")), right.set_state_release))

	return events


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
		self.scheduler((self.check_state_hold, timeout+time.time()))


class Events(object):

	"""
	Main Class for this module. Initializes default events. it is also possible
	to dynamically update, add -or remove events at runtime.
	"""

	def __init__(self, queue):

		self.list = []
		self.queue = queue
		self.index = Index()

		# add events
		self.list.extend(init_buttons(factory=ButtonFactory(self.schedule), index=self.index.inc))

	def schedule(self, task):
		self.queue.put(task)

	def bind_event(self, signal=None, event=None):

		"""
		Add one event to list.

		Append a 3-tuple: (<INDEX>, <SIGNAL>=(src, dst, data), <EVENT>)
		"""

		self.list.append((self.index.inc(), signal, event))

	def unbind_event(self, index):

		"""
		Remove one event, with index as reference.
		"""

		self.list.remove(index)

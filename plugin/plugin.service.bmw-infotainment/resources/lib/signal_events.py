"""
Handle initialization of all events, also implements methods for adding
and removing events at runtime.
"""
import kodi.builtin
import signaldb
import main_thread
import log as log_module

from kodi import gui
from bmw import KombiInstrument, CDChanger
from buttons import Button

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


# TODO: move to another module..
def init_basic_controls(bind_event):

	"""
	Initialize all events for buttons.
	"""

	src, dst = "IBUS_DEV_BMBT", None

	# regular expression for scroll speed (forwarded speed to method)
	regexp = "([1-9])"

	right_knob = Button(hold=kodi.builtin.action("back"), release=kodi.builtin.action("Select"))
	bind_event(signaldb.create((src, dst, "right-knob.push")), right_knob.set_state_push)
	bind_event(signaldb.create((src, dst, "right-knob.hold")), right_knob.set_state_hold)
	bind_event(signaldb.create((src, dst, "right-knob.release")), right_knob.set_state_release)

	bind_event(signaldb.create((src, dst, "right-knob.turn-left"), SCROLL_SPEED=regexp), kodi.builtin.scroll("up"))
	bind_event(signaldb.create((src, dst, "right-knob.turn-right"), SCROLL_SPEED=regexp), kodi.builtin.scroll("down"))

	left = Button(push=kodi.builtin.action("Left"), hold=kodi.builtin.action("Left"))
	bind_event(signaldb.create((src, dst, "left.push")), left.set_state_push)
	bind_event(signaldb.create((src, dst, "left.hold")), left.set_state_hold)
	bind_event(signaldb.create((src, dst, "left.release")), left.set_state_release)

	right = Button(push=kodi.builtin.action("Right"), hold=kodi.builtin.action("Right"))
	bind_event(signaldb.create((src, dst, "right.push")), right.set_state_push)
	bind_event(signaldb.create((src, dst, "right.hold")), right.set_state_hold)
	bind_event(signaldb.create((src, dst, "right.release")), right.set_state_release)

	bind_event(signaldb.create((src, dst, "info.push")), open_or_close_win, gui.AddonOverview)


# TODO: move to another module..
def open_or_close_win(Window):

	win = gui.window_stack.pop(Window.__name__, None)

	if win:
		win.close()
		del win
	else:
		gui.close_all_windows()
		main_thread.add(gui.open_window, Window)


class Events(object):

	"""
	Callbacks to be triggered from a received signal. also containing
	methods for to dynamically update, add -or remove events at runtime.
	"""

	INDEX, SIGNAL, METHOD, ARGS, KWARGS = range(5)

	def __init__(self, send):

		self.send = send
		self.events = []
		self.index = Index()

		# devices
		self.cd_changer = CDChanger(send)
		self.kombi_instrument = KombiInstrument(send)

	def initialize_events(self):

		"""
		Initial events launched when system is just started (called from service.py)!
		"""

		init_basic_controls(self.bind_event)

		self.kombi_instrument.init_events(self.bind_event)
		self.cd_changer.init_events(self.bind_event)

	def bind_event(self, signal, method, *args, **kwargs):

		"""
		Add one event to list. if keyword argument "static=False" is used, event will
		be deleted from list after execution (one-time event)
		"""

		index = self.index.inc()
		item = (index, signal, method, args, kwargs)

		self.events.append(item)
		return index

	def unbind_event(self, ref):

		"""
		Remove one event, with index as reference.
		"""

		for item in self.events:

			index = item[Events.INDEX]

			if index == ref:
				self.events.remove(item)
				return index

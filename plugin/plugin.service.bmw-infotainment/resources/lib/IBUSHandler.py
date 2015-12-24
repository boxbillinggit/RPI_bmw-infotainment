"""
This module map events against IBUS-message
"""

# TODO rename module to "EventHandler"
import threading
import Queue
from BMButtons import Button
import kodi
import time
from TCPIPSocket import to_hexstr
import signaldb as signal

import log as log_module
log = log_module.init_logger(__name__)

try:
	import xbmc, xbmcplugin, xbmcgui, xbmcaddon

except ImportError as err:
	import debug.xbmc as xbmc
	import debug.xbmcgui as xbmcgui
	import debug.xbmcaddon as xbmcaddon

__author__ 		= 'Lars'
__monitor__ 	= xbmc.Monitor()
__addon__		= xbmcaddon.Addon()
__addonname__	= __addon__.getAddonInfo('name')
__addonid__		= __addon__.getAddonInfo('id')
__addonpath__	= __addon__.getAddonInfo('path')



def match_found(bus_sig, event_sig):

	"""
	Return True if a match between received signal and an event is found.

	"None" means match all (don't evaluate), but data must exist and be equal!
	"""

	src, dst, data = event_sig
	bus_src, bus_dst, bus_data = bus_sig

	return not (
		(src and bus_src != src) or
		(dst and bus_dst != dst) or
		(bus_data != data)
	)

# TODO: where to instantiate?
queue = Queue.Queue()


class EventHandler(threading.Thread):

	"""
	This class runs in a separate worker thread and processes queued signal events.

	Event constructor. This class initialize all default events mapped against signal.
	it is also possible to dynamically update, add -or remove events at runtime.
	"""

	POLL = 0.2

	def __init__(self):
		super(EventHandler, self).__init__()
		self.queue = queue
		self.schedule = []
		self.event = []

		self.init_events()

	def bind_event(self, sig=None, event=None):

		"""
		Add events with an index to tuple?: (<INDEX>, <SIGNAL>*, <EVENT>)

		*<SIGNAL>=(src, dst, data)
		"""

		# TODO: add index also?
		self.event.extend(zip(sig, event))

	def unbind_event(self, index):
		pass

	def init_events(self):
		"""
		Bind events: awful right now..

		"""

		right_knob = Button(queue=self.queue, hold=kodi.action("back"), release=kodi.action("enter"))
		self.bind_event(
			sig=signal.create_from_tuple(zip(["IBUS_DEV_BMBT"]*5, [None]*5, map(lambda nspace: "right-knob.{}".format(nspace), ["push", "hold", "release", "turn-left", "turn-right"]))),
			event=[right_knob.set_state_push, right_knob.set_state_hold, right_knob.set_state_release, kodi.action("up"), kodi.action("down")]
		)

		left = Button(queue=self.queue, hold=kodi.action("Left"), release=kodi.action("Left"))
		self.bind_event(
			sig=signal.create_from_tuple(zip(["IBUS_DEV_BMBT"]*3, [None]*3, map(lambda nspace: "left.{}".format(nspace), ["push", "hold", "release"]))),
			event=[left.set_state_push, left.set_state_hold, left.set_state_release]
		)

		right = Button(queue=self.queue, hold=kodi.action("Right"), release=kodi.action("Right"))
		self.bind_event(
			sig=signal.create_from_tuple(zip(["IBUS_DEV_BMBT"]*3, [None]*3, map(lambda nspace: "right.{}".format(nspace), ["push", "hold", "release"]))),
			event=[right.set_state_push, right.set_state_hold, right.set_state_release]
		)

	def check_schedule(self):

		"""
		Check time schedule if any tasks needs to be executed
		"""

		for task in self.schedule:

			event, event_time = task

			if (event_time is None) or (time.time() >= event_time):

				try:
					event()
				except TypeError as error:
					log.error("{} - {}".format(self.__class__.__name__, error))

				self.schedule.remove(task)
				# log.debug("{} - events to schedule {}".format(self.__class__.__name__, len(self.schedule)))

	def run(self):

		"""
		thread's activity - handle events from queue. If we have an scheduled event, get() is polled
		periodically, else we block until new object is available on queue.
		"""

		while True:
			timeout = (EventHandler.POLL if len(self.schedule) else None)

			self.check_schedule()

			try:
				task = self.queue.get(timeout=timeout)
			except Queue.Empty:
				continue

			self.schedule.append(task)
			self.queue.task_done()


class Filter(object):

	"""
	This is the main class -and routes all BUS-messages to a matching event (if defined)
	"""

	def __init__(self):

		self.events = EventHandler()
		self.events.setDaemon(True)
		self.events.start()

	def handle_event(self, bus_sig):

		"""
		Received bus signal from TCP/IP socket. Compare if we have matching events.
		If event is found, put on event queue scheduled to execute now -and stop searching.

		Signal is 3-tuple: (src, dst, data).
		events.put_on_queue(<event-method>, <scheduled-time>)
		"""

		src, dst, data = bus_sig

		for event_sig, event in self.events.event:

			if match_found(bus_sig, event_sig):
				self.events.queue.put((event, None))
				log.debug("{} - match for signal {}".format(self.__class__.__name__, to_hexstr(src+dst+data)))
				break

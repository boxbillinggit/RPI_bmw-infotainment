"""
This module map events against IBUS-message
"""
# TODO rename module to "EventHandler" or "ibushandler" ?

import threading
import Queue
import time

# import local modules
from TCPIPSocket import to_hexstr
from events import Events
import log as log_module
log = log_module.init_logger(__name__)


def match_found(bus_sig, event_sig):

	"""
	Return "True" if a match between received signal and an event is found.

	"None" means match all (don't evaluate), but data must exist and be equal!
	"""

	src, dst, data = event_sig
	bus_src, bus_dst, bus_data = bus_sig

	return not (
		(src and bus_src != src) or
		(dst and bus_dst != dst) or
		(bus_data != data)
	)


class EventHandler(threading.Thread):

	"""
	This class runs in a separate worker thread and processes all queued tasks.
	"""

	Queue = Queue.Queue()

	# task enumerated
	EVENT, TIME = range(2)
	POLL = 0.2

	def __init__(self):
		super(EventHandler, self).__init__()
		self.queue = EventHandler.Queue
		self.schedule = []

	def check_schedule(self):

		"""
		Check if any scheduled tasks is in time to be executed.
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

	def reschedule(self, task):

		"""
		Append new task to schedule, or re-schedule task with a new time (events
		is allowed to be scheduled only once).
		"""

		for sched_task in self.schedule:

			if task[EventHandler.EVENT] == sched_task[EventHandler.EVENT]:
				# log.debug("{} - rescheduling task".format(self.__class__.__name__))
				self.schedule.remove(sched_task)

		self.schedule.append(task)

	def run(self):

		"""
		Thread's main activity - consume tasks from queue. If task remains scheduled
		in future we poll periodically. Else if schedule-list is empty we block
		until new tasks is available on queue.
		"""

		while True:

			self.check_schedule()

			timeout = EventHandler.POLL if len(self.schedule) else None

			try:
				task = self.queue.get(timeout=timeout)
			except Queue.Empty:
				continue

			self.reschedule(task)
			self.queue.task_done()


class Filter(object):

	"""
	Main class for this module. Filter BUS-messages to a matching event (if defined)
	"""

	def __init__(self):

		self.event_handler = EventHandler()
		self.event_handler.daemon = True
		self.event_handler.start()

		self.events = Events(EventHandler.Queue)

	def handle_signal(self, bus_sig):

		"""
		Handles bus signals received from TCP/IP socket. Compare if we have a matching
		event. If match found, put task on event queue (None=scheduled to execute now)
		and stop searching.

		Signal is 3-tuple: (src, dst, data)
		"""

		src, dst, data = bus_sig

		for index, event_sig, event in self.events.list:

			if match_found(bus_sig, event_sig):
				self.event_handler.queue.put((event, None))
				log.debug("{} - match for signal {}".format(self.__class__.__name__, to_hexstr(src+dst+data)))
				break

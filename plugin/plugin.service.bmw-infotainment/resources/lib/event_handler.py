"""
This module handle events in a separate thread.
"""

import threading
import Queue
import time

try:
	import xbmc
except ImportError as err:
	import debug.xbmc as xbmc

import log as log_module
log = log_module.init_logger(__name__)

__author__ 		= 'Lars'
__monitor__ 	= xbmc.Monitor()

# item on queue enumerated
METHOD, TIMESTAMP, ARGS, KWARGS = range(4)


class Scheduler(object):

	"""
	Interface for adding, removing -or rescheduling items in schedule.
	"""

	def __init__(self, queue=None):
		self.queue = queue or EventHandler.Queue

	def add(self, event, *args, **kwargs):
		self.queue.put((event, args, kwargs))

	def remove(self):
		pass


class EventHandler(threading.Thread):

	"""
	This class runs in a separate worker thread and processes all queued tasks.
	"""

	Queue = Queue.Queue()

	POLL_IDLE = 1.0
	POLL_TASK = 0.2

	def __init__(self, queue=None):
		super(EventHandler, self).__init__()
		self.daemon = True
		self.queue = queue or EventHandler.Queue
		self.schedule = []

	def check_schedule(self):

		"""
		Check if any scheduled tasks is in time to be executed.
		"""

		for task in self.schedule:

			timestamp = task[TIMESTAMP]

			if (timestamp is None) or (time.time() >= timestamp):

				method, args, kwargs = task[METHOD], task[ARGS], task[KWARGS]

				try:
					method(*args, **kwargs)
				except TypeError as error:
					log.error("{} - {}".format(self.__class__.__name__, error))

				self.schedule.remove(task)
				# log.debug("{} - events to schedule {}".format(self.__class__.__name__, len(self.schedule)))

	def reschedule(self, method):

		"""
		remove task for rescheduling with a new time (event is allowed to be scheduled only once).
		"""

		for task in self.schedule:

			if method == task[METHOD]:
				# log.debug("{} - rescheduling task".format(self.__class__.__name__))
				self.schedule.remove(task)

	def schedule_task(self, method, *args, **kwargs):

		"""
		Append new task to schedule, re-schedule task with a new time if requested (default True).
		"""

		if kwargs.pop("reschedule", True):
			self.reschedule(method)

		self.schedule.append((method, kwargs.pop("timestamp", None), args, kwargs))

	def run(self):

		"""
		Thread's main activity - consume tasks from queue. If task remains scheduled
		in future we poll periodically. If schedule-list is empty we also poll
		but with a longer interval . We must poll periodically even with no tasks in
		schedule since the blocking get() won't let us terminate the thread.
		"""

		while not __monitor__.abortRequested():

			self.check_schedule()

			timeout = EventHandler.POLL_TASK if len(self.schedule) else EventHandler.POLL_IDLE

			try:
				method, args, kwargs = self.queue.get(timeout=timeout)
			except Queue.Empty:
				continue

			self.schedule_task(method, *args, **kwargs)
			self.queue.task_done()

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

# import local modules
import log as log_module
log = log_module.init_logger(__name__)

__author__ 		= 'Lars'
__monitor__ 	= xbmc.Monitor()


class EventHandler(threading.Thread):

	"""
	This class runs in a separate worker thread and processes all queued tasks.
	"""

	Queue = Queue.Queue()

	# task enumerated
	EVENT, TIME = range(2)

	POLL_IDLE = 1.0
	POLL_TASK = 0.2

	def __init__(self, queue=None):
		super(EventHandler, self).__init__()
		self.queue = queue or EventHandler.Queue
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
		in future we poll periodically. If schedule-list is empty we also poll
		but with a longer interval . We must poll periodically even with no tasks in
		schedule since the blocking get() won't let us terminate the thread.
		"""

		while not __monitor__.abortRequested():

			self.check_schedule()

			timeout = EventHandler.POLL_TASK if len(self.schedule) else EventHandler.POLL_IDLE

			try:
				task = self.queue.get(timeout=timeout)
			except Queue.Empty:
				continue

			self.reschedule(task)
			self.queue.task_done()

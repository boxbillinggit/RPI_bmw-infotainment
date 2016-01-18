"""
This module handle all events in a separate thread.
"""

import threading
import Queue
import time
import log as log_module

try:
	import xbmc
except ImportError as err:
	import debug.xbmc as xbmc

log = log_module.init_logger(__name__)
queue = Queue.Queue()

__author__ 		= 'Lars'
__monitor__ 	= xbmc.Monitor()

# item on queue
METHOD, TIMESTAMP, INTERVAL, ARGS, KWARGS = range(5)


def add(method, *args, **kwargs):

	"""
	Used for scheduling an event. following keyword-argument is used internally
	and will not be forwarded to method;

		interval	= [None]  - interval for periodic tasks
		timestamp	= [None]  - time when task shall be executed.
		remove		= [False] - remove task
		reschedule	= [True]  - reschedule task if already exists in schedule (allows method to be scheduled
								only once).
	"""

	queue.put((method, args, kwargs))


def remove(method):

	"""
	Used for removing an event from schedule.
	"""

	queue.put((method, (), {"remove": True}))


class EventHandler(threading.Thread):

	"""
	This class runs in a separate worker thread and processes all queued tasks.
	"""

	POLL_IDLE = 1.0
	POLL_TASK = 0.2

	def __init__(self, new_queue=None):
		super(EventHandler, self).__init__()
		self.daemon = True
		self.queue = new_queue or queue
		self.schedule = []

	def check_schedule(self):

		"""
		Check if any scheduled tasks is in time to be executed. if method returns true we
		reschedule task.
		"""

		periodic_tasks = []

		for task in self.schedule:

			now = time.time()
			timestamp = task[TIMESTAMP]
			reschedule = False

			if (timestamp is None) or (now >= timestamp):

				method, interval, args, kwargs = task[METHOD], task[INTERVAL], task[ARGS], task[KWARGS]

				try:
					reschedule = method(*args, **kwargs)
				except TypeError as error:
					log.error("{} - {}".format(self.__class__.__name__, error))

				self.schedule.remove(task)

				if reschedule and interval:

					# if something goes wrong and system locks for a long while, we don't want to accumulate periodic tasks.
					if timestamp and (now - timestamp) > interval:
						log.warning("{} - System busy, periodic task were missed".format(self.__class__.__name__))
						timestamp = now

					periodic_tasks.append((method, (timestamp or now)+interval, interval, args, kwargs))

				# log.debug("{} - events to schedule {}".format(self.__class__.__name__, len(self.schedule)))

		self.schedule.extend(periodic_tasks)

	def unschedule(self, method):

		"""
		remove task (e.g. before rescheduling with a new time).
		"""

		for task in self.schedule:

			if method == task[METHOD]:
				# log.debug("{} - rescheduling task".format(self.__class__.__name__))
				self.schedule.remove(task)

	def handle_task(self, method, *args, **kwargs):

		"""
		Append, remove or reschedule task.
		"""

		remove, reschedule = kwargs.pop("remove", False), kwargs.pop("reschedule", True)

		if reschedule or remove:
			self.unschedule(method)

		if not remove:
			self.schedule.append((method, kwargs.pop("timestamp", None), kwargs.pop("interval", None), args, kwargs))

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

			self.handle_task(method, *args, **kwargs)
			self.queue.task_done()

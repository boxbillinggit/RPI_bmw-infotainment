"""
Main-thread handle blocking GUI-callbacks, etc..
"""

import Queue
import log as log_module

log = log_module.init_logger(__name__)

__author__ = 'lars'


def add(method, *args, **kwargs):

	""" Used for scheduling an event """

	MainThread.Queue.put((method, args, kwargs), False)


# def remove(method):
#
# 	"""
# 	Used for removing an event from schedule.
# 	"""
#
# 	MainThread.Queue.put((method, (), {"remove": True}))

def default_condition():

	""" Default condition for running thread """

	return True


class MainThread(object):

	"""
	Main thread's activity. Blocking until shutdown is requested.
	"""

	Queue = Queue.Queue()
	POLL = 0.2

	def __init__(self, queue=None, condition=None, handle_exit=None):
		self.name = "MainThread"
		self.queue = queue or MainThread.Queue

		self.still_alive = condition or default_condition
		self.handle_exit = handle_exit

	def start(self):

		"""
		Some events must be handled from main-thread..
		"""

		while self.still_alive():

			try:
				method, args, kwargs = self.queue.get(timeout=self.POLL)
			except Queue.Empty:
				continue

			method(*args, **kwargs)
			# log.debug("Executing from thread: {thread} event {event}".format(thread=threading.currentThread().getName(), event=method))
			self.queue.task_done()

		if self.handle_exit:
			self.handle_exit()

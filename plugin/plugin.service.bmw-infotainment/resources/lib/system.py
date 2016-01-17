import time

import kodi
import log as log_module
import settings

log = log_module.init_logger(__name__)
__author__ = 'lars'


class State(object):

	"""
	Interface for controlling system shutdown, etc
	"""

	SHUTDOWN, INIT = range(2)

	def __init__(self, scheduler):
		self.state = State.INIT
		self.scheduler = scheduler

	def set_state_init(self):

		""" Driver came back within time, abort shutdown """

		if self.state == State.SHUTDOWN:
			self.scheduler.remove(kodi.shutdown)
			log.info("{} - Welcome back! (Aborting system shutdown request)".format(self.__class__.__name__))

		self.state = State.INIT

	def set_state_shutdown(self):

		""" Schedule shutdown when key has been pulled out from ignition lock """

		if self.state == State.INIT:

			shutdown = settings.System.IDLE_SHUTDOWN

			self.scheduler.add(kodi.shutdown, timestamp=time.time()+shutdown)
			log.info("{} - System shutdown is scheduled within {} min".format(self.__class__.__name__, (shutdown/60)))

		self.state = State.SHUTDOWN

"""
This module contains a constructor class for creating buttons
requiring a state-machine.
"""

#TODO: rename module to "StateButton"

import time
import threading, Queue

import log as log_module
log = log_module.init_logger(__name__)

__author__ = 'Lars'


# http://www.laurentluce.com/posts/python-threads-synchronization-locks-rlocks-semaphores-conditions-events-and-queues/
# http://stackoverflow.com/questions/9190169/threading-and-information-passing-how-to

# one thread for handling state HOLD (periodically executing action while holding)

#Ref:
#http://stackoverflow.com/questions/16044452/sharing-data-between-threads-in-python
#https://pymotw.com/2/threading/


class State(object):

	"""
	Object containing current state, new object for each Button.
	"""

	# define timings for state HOLD - unit in [seconds]
	HOLD_INIT = 2.0
	HOLD_PERIODIC = 0.5
	HOLD_ABORT = 5.0

	# define enumerated states
	STATE = ["PUSH", "HOLD", "RELEASE"]
	PUSH, HOLD, RELEASE = range(len(STATE))

	def __init__(self):
		self.state = State.RELEASE


class Button(object):

	"""
	Pre-defined states for object Button:
		* push
		* hold
		* release
	"""

	def __init__(self, queue=None, push=None, hold=None, release=None):

		# actions
		self.push = push
		self.hold = hold
		self.release = release

		state = State()

		# initial conditions
		self.timestamp = time.time()
		self.state = state.state
		self.queue = queue

	def still_holding(self):

		"""
		Check if we're holding button long enough -and limit the max time for execute
		action in state 'HOLD'
		"""

		# return State.HOLD_INIT < (time.time() - self.timestamp) < State.HOLD_ABORT
		return (time.time() - self.timestamp) < State.HOLD_ABORT

	def schedule_check_state_hold(self, timeout=State.HOLD_INIT):
		print "schedule_check_state_hold() "
		# TODO: must prevent that previous scheduled events don't get executed.
		self.queue.put((self.check_state_hold, timeout+time.time()))

	def check_state_hold(self):

		"""
		This is called from event-thread and evaluates if we are about to
		change state from 'PUSH' to 'HOLD'. Execute action periodically (max time-
		limited) by re-schedule event while current state is 'HOLD'

		most of the buttons is broadcasting state 'HOLD' once after 1s -  hence
		different initial sleep times below to not interfering with this event.
		"""

		# log.debug("{} - check_state_hold() - still holding? (current state  '{}')'".format(self.__class__.__name__, State.STATE[self.state]))

		if self.state != State.RELEASE and self.still_holding():
			self.schedule_check_state_hold(timeout=State.HOLD_PERIODIC)
			self.set_state_hold()

	def set_state_push(self):

		"""
		Current state is 'PUSH'

		Execute action if defined, and if previous state was 'RELEASE'. we start to
		evaluate if we're pushing long enough to enter state 'HOLD' (but only
		if we have an action for state 'HOLD').
		"""

		if self.push and self.state == State.RELEASE:
			self.push()

		if self.hold and self.state == State.RELEASE:
			self.timestamp = time.time()
			self.schedule_check_state_hold()

		self.state = State.PUSH

	def set_state_hold(self):

		"""
		Current state is 'HOLD' - execute action if defined and only if previous state was
		push or hold (not RELEASE).
		"""

		if self.hold and self.state != State.RELEASE:
			self.hold()

		self.state = State.HOLD

	def set_state_release(self):

		"""
		Current state is 'RELEASE' - execute action only if previous state
		was 'PUSH' (and if action is defined).
		"""

		if self.release and self.state == State.PUSH:
			self.release()

		self.state = State.RELEASE

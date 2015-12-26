"""
This module contains a class used as template for constructing buttons
with a state-machine.
"""

import time

# import local modules
import log as log_module
log = log_module.init_logger(__name__)

__author__ = 'Lars'


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
		* PUSH
		* HOLD
		* RELEASE

	This class should only be used as template and is preferably instantiated from
	a subclass, since "schedule_check_state_hold" must be implemented accordingly.
	"""

	def __init__(self, push=None, hold=None, release=None):

		# actions
		self.push = push
		self.hold = hold
		self.release = release

		state = State()

		# initial conditions
		self.timestamp = time.time()
		self.state = state.state

	def still_holding(self):
		return (time.time() - self.timestamp) < State.HOLD_ABORT

	def schedule_check_state_hold(self, timeout=None):
		"""
		Overridden in constructor's subclass. This function handles
		event scheduling for evaluating if we should make transition
		to state 'HOLD'..
		"""
		pass

	def check_state_hold(self):

		"""
		This is called from event-thread and evaluates if we are about to
		change state from 'PUSH' to 'HOLD', but also execute action for HOLD
		periodically (max time-limited) by re-schedule this function while
		current state is 'HOLD'

		Most of the buttons is broadcasting state 'HOLD' once after 1s -  hence
		different initial sleep times to avoid interfering with this event.
		"""

		# log.debug("{} - check_state_hold() - still holding? (current state  '{}')'".format(self.__class__.__name__, State.STATE[self.state]))

		if self.state != State.RELEASE and self.still_holding():
			self.schedule_check_state_hold(timeout=State.HOLD_PERIODIC)
			self.set_state_hold()

	def set_state_push(self):

		"""
		Current state is 'PUSH'

		Execute action if defined. If previous state was 'RELEASE'. we start to
		evaluate if we're pushing long enough for changing state to 'HOLD' (but
		only if we have an action for state 'HOLD').
		"""

		if self.push and self.state == State.RELEASE:
			self.push()

		if self.hold and self.state == State.RELEASE:
			self.timestamp = time.time()
			self.schedule_check_state_hold()

		self.state = State.PUSH

	def set_state_hold(self):

		"""
		Current state is 'HOLD' - execute action only if previous state was
		'PUSH' or 'HOLD' (not RELEASE), and if an action is defined.
		"""

		if self.hold and self.state != State.RELEASE:
			self.hold()

		self.state = State.HOLD

	def set_state_release(self):

		"""
		Current state is 'RELEASE' - execute action only if previous state
		was 'PUSH' (and if an action is defined).
		"""

		if self.release and self.state == State.PUSH:
			self.release()

		self.state = State.RELEASE

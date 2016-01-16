"""
This module contains a class used as template for constructing buttons
with a state-machine.
"""

import settings
import log as log_module

log = log_module.init_logger(__name__)

__author__ = 'Lars'


class State(object):

	"""
	Object containing current state, new object for each Button.
	"""

	# define enumerated states
	STATE = ["PUSH", "HOLD", "RELEASE"]
	PUSH, HOLD, RELEASE = range(3)

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

	def __init__(self, push=None, hold=None, release=None, max_holdings=None):

		# actions
		self.push = push
		self.hold = hold
		self.release = release
		self.max_holdings = max_holdings or settings.Buttons.STATE_HOLD_N_MAX

		state = State()

		# initial conditions
		self.holding = 0
		self.state = state.state

	def schedule_check_state_hold(self):
		"""
		Overridden in subclass. method for scheduling "check_state_hold" periodically.
		"""
		pass

	def check_state_hold(self):

		"""
		This is called periodically from scheduler and evaluates if we are about to
		change state from 'PUSH' to 'HOLD'. Also execute action for HOLD
		periodically (max-limited). Reschedule event as long as method returns "True"

		Most of the buttons is broadcasting state 'HOLD' once after 1s -  hence
		different initial time-intervals to avoid interfering with this event.
		"""

		# log.debug("{} - check_state_hold() - still holding? (current state  '{}')'".format(self.__class__.__name__, State.STATE[self.state]))

		self.holding += 1

		if self.state != State.RELEASE and self.holding <= self.max_holdings:
			self.set_state_hold()
			return True

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
			self.holding = 0
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

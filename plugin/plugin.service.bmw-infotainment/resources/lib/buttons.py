"""
This module contains a class used as template for constructing buttons
with a state-machine.
"""
import time
import event_handler
import settings
import log as log_module
from statemachine import StateMachine

log = log_module.init_logger(__name__)

__author__ = 'Lars'


class State(StateMachine):

	"""
	Object containing current state, new object for each Button.
	"""

	states = ("PUSH", "HOLD", "RELEASE")

	PUSH, HOLD, RELEASE = range(3)

	def __init__(self):
		super(State, self).__init__(State.RELEASE)

		self.transitions = \
			{"from": (State.PUSH,), 	"to": (State.HOLD, State.RELEASE)}, \
			{"from": (State.HOLD,), 	"to": (State.HOLD, State.RELEASE)}, \
			{"from": (State.RELEASE,), 	"to": (State.PUSH,)}


class Button(State):

	"""
	Button object. This class should only be used as template and is preferably
	instantiated from a subclass, since "schedule_check_state_hold" must be
	implemented accordingly.
	"""

	def __init__(self, push=None, hold=None, release=None, max_holdings=None):
		State.__init__(self)

		# methods
		self.push = push
		self.hold = hold
		self.release = release

		# initial conditions
		self.holding = 0
		self.max_holdings = max_holdings or settings.Buttons.STATE_HOLD_N_MAX

	def schedule_check_state_hold(self):

		"""
		Method for scheduling "check_state_hold" periodically.
		"""

		# log.debug("{} -schedule_check_state_hold() ".format(self.__class__.__name__))
		timestamp = time.time()+settings.Buttons.STATE_HOLD_INIT
		event_handler.add(self.check_state_hold, timestamp=timestamp, interval=settings.Buttons.STATE_HOLD_INTERVAL)

	def check_state_hold(self):

		"""
		This is called periodically from scheduler and evaluates if we are about to
		change state from 'PUSH' to 'HOLD'. Also execute action for HOLD
		periodically (max-limited). Reschedule event as long as method returns "True"

		Most of the buttons is broadcasting state 'HOLD' once after 1s -  hence
		different initial time-intervals to avoid interfering with this event.
		"""

		# log.debug("{} - check_state_hold() - still holding? (current state  '{}')'".format(self.__class__.__name__, self.translate_State()))

		self.holding += 1

		if self.state_is(State.RELEASE) or self.holding > self.max_holdings:
			return

		self.set_state_hold()

		# reschedule event
		return True

	def set_state_push(self):

		"""
		Current state is 'PUSH'

		Execute action if defined. If previous state was 'RELEASE'. we start to
		evaluate if we're pushing long enough for changing state to 'HOLD' (but
		only if we have an action for state 'HOLD').
		"""

		if not self.set_state_to(State.PUSH):
			return

		if self.push:
			self.push()

		if self.hold:
			self.holding = 0
			self.schedule_check_state_hold()

	def set_state_hold(self):

		"""
		Current state is 'HOLD' - execute action only if previous state was
		'PUSH' or 'HOLD' (not RELEASE), and if an action is defined.
		"""

		if self.set_state_to(State.HOLD) and self.hold:
			self.hold()

	def set_state_release(self):

		"""
		Current state is 'RELEASE' - execute action only if previous state
		was 'PUSH' (and if an action is defined).
		"""

		if self.state_is(State.PUSH) and self.release:
			self.release()

		self.set_state_to(State.RELEASE)

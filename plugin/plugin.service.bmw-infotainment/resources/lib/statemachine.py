import log as log_module


log = log_module.init_logger(__name__)
__author__ = 'lars'


class State(object):

	"""
	Minimalistic statemachine.
	"""

	states = []

	def __init__(self, state):

		self.state = state
		self.transitions = ()

	def state_is(self, state):

		""" shortcut for comparing with current state """

		return self.state is state

	def translate_state(self, state=None):

		""" translate current state (or state provided from argument) to a string """

		return self.states[state if state else self.state]

	def set_state_to(self, new_state):

		"""
		Returns "True" if transition is allowed, and also update current state.
		"""

		for transition in self.transitions:

			if self.state in transition.get("from") and new_state in transition.get("to"):
				# log.debug("State {} -> {}".format(States.state[self.state], new_state))
				self.state = new_state
				return True

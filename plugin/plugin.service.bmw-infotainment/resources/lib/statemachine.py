import log as log_module


log = log_module.init_logger(__name__)
__author__ = 'lars'


class StateMachine(object):

	"""
	Minimalistic state-machine.
	"""

	states = ()

	def __init__(self, state, on_new_state=None, debug=False):
		self.debug = debug
		self.state = state
		self.on_new_state = on_new_state
		self.transitions = ()

	def state_is(self, state):

		""" shortcut for comparing with current state """

		return self.state is state

	def translate_state(self, state=None):

		""" translate current state (or state provided from argument) to a string """

		return self.states[state if state else self.state]

	def set_state_to(self, new_state):

		"""
		Returns "True" if transition is allowed, and also update current state. Possible to
		add callback-function for successfully changing state.
		"""

		for transition in self.transitions:

			if self.state in transition.get("from") and new_state in transition.get("to"):

				if self.debug:
					log.debug("Class: {} - State {} -> {}".format(self.__class__.__name__, self.states[self.state], self.states[new_state]))

				if self.on_new_state:
					self.on_new_state(new_state)

				self.state = new_state
				return True

import time
import log as log_module
import settings
import event_handler

from statemachine import StateMachine
from kodi import builtin as kodi

log = log_module.init_logger(__name__)
__author__ = 'lars'


# TODO: finish this
class State(StateMachine):

	"""
	Interface for controlling system shutdown, etc
	"""

	INIT, SHUTDOWN = range(2)

	# MID-states
	states = ("UNDEFINED", "MENU", "RADIO", "CD", "TAPE")

	UNDEFINED, MENU, RADIO, CD, TAPE = range(5)

	def __init__(self):
		super(State, self).__init__(State.UNDEFINED)

		self.transitions = \
			{"from": (State.UNDEFINED,), "to": (State.MENU, State.RADIO, State.CD, State.TAPE)}, \
			{"from": (State.RADIO,), 	"to": (State.CD,)}, \
			{"from": (State.CD,), 		"to": (State.TAPE,)}, \
			{"from": (State.TAPE,), 	"to": (State.MENU,)}, \
			{"from": (State.MENU,), 	"to": (State.RADIO,)}

		# we expecting a state change only when button is pressed
		self.transition_allowed = False
		self.sys_state = State.INIT

	def button_pressed(self):
		self.transition_allowed = True

	def set_state_init(self):

		""" Driver came back within time, abort shutdown """

		if self.sys_state == State.SHUTDOWN:
			event_handler.remove(kodi.shutdown)
			log.info("{} - Welcome back! (Aborting system shutdown request)".format(self.__class__.__name__))

		self.sys_state = State.INIT

	def set_state_shutdown(self):

		""" Schedule shutdown when key has been pulled out from ignition lock """

		if self.sys_state == State.INIT:

			shutdown = settings.System.IDLE_SHUTDOWN

			event_handler.add(kodi.shutdown, timestamp=time.time()+shutdown)
			log.info("{} - System shutdown is scheduled within {} min".format(self.__class__.__name__, (shutdown/60)))

		self.sys_state = State.SHUTDOWN

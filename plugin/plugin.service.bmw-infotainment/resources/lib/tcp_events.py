import time
import threading

import kodi
import gateway_protocol
import tcp_socket
import event_handler
import log as log_module

try:
	import xbmc
except ImportError:
	import debug.xbmc as xbmc

log = log_module.init_logger(__name__)
Protocol = gateway_protocol.Protocol
TCPIPSettings = kodi.TCPIPSettings
tcp_settings = kodi.TCPIPSettings()


__author__		= 'lars'
__monitor__ 	= xbmc.Monitor()

TIME_INTERVAL_PING = 3
TIME_RECONNECT = 15
ALIVE_TIMEOUT = 10
MAX_ATTEMPTS = 5


def state(string):
	return States.state.index(string)


def next_check():
	return time.time() + TIME_INTERVAL_PING


def next_reconnect():
	return time.time() + TIME_RECONNECT


class States(object):

	"""
	Current state on TCP-connection.
	"""

	state = ["INIT", "REROUTING", "CONNECTING", "CONNECTED", "DISCONNECTED", "RECONNECTING"]

	def __init__(self):
		self.state = state("INIT")
		self.transitions = \
			{"from": ("INIT",),         "to": ("REROUTING", "DISCONNECTED")}, \
			{"from": ("REROUTING",),    "to": ("CONNECTING",)}, \
			{"from": ("CONNECTING",),   "to": ("CONNECTED", "DISCONNECTED")}, \
			{"from": ("CONNECTED",),    "to": ("DISCONNECTED",)}, \
			{"from": ("DISCONNECTED",), "to": ("RECONNECTING", "INIT")}, \
			{"from": ("RECONNECTING",), "to": ("INIT",)}

	def state_is(self, current_state):
		return self.state is States.state.index(current_state)

	def set_state_to(self, new_state):

		"""
		Minimalistic state-machine. Returns "True" if transition is allowed,
		and also update current state.
		"""

		for transition in self.transitions:

			if States.state[self.state] in transition.get("from") and new_state in transition.get("to"):
				# log.debug("State {} -> {}".format(States.state[self.state], new_state))
				self.state = state(new_state)
				return True

		return False


class Request(object):

	"""
	Current request from user.
	"""

	RUNNING, STOPPED = range(2)

	def __init__(self):
		self.current_request = Request.RUNNING


class Events(gateway_protocol.Protocol, tcp_socket.ThreadedSocket, States):

	"""
	Base class for handling all events regarding the TCP/IP-layer via a
	state-machine.
	"""

	# TODO: use acquire/release lock (notify, wait) instead of "event"??
	Event = threading.Event()
	POLL = 1

	def __init__(self, event=None, queue=None):
		States.__init__(self)
		gateway_protocol.Protocol.__init__(self)
		tcp_socket.ThreadedSocket.__init__(self)

		self.event = event or Events.Event
		self.queue = queue or event_handler.EventHandler.Queue

		self.host = tcp_settings.get_host()
		self.timestamp = time.time()
		self.attempts = 0

		request = Request()
		self.request = request.current_request

	def start_service(self):

		"""
		Used to start -or restart service (from user -or event-handler).
		"""

		if self.request is Request.STOPPED:
			return

		if self.set_state_to("INIT"):
			self.host = tcp_settings.get_host()
			self.timestamp = time.time()
			self.event.set()

	def stop_service(self):

		"""
		Request from user to disconnect. Broadcast disconnect to gateway
		and the server will disconnect us gracefully.
		"""

		if self.state_is("CONNECTED"):
			self.sendall(Protocol.DISCONNECT)

	def reset_attempts(self):
		""" Called only when user requests to connect """
		self.attempts = 0

	def reconnect(self):
		return self.request is Request.RUNNING and (self.attempts < MAX_ATTEMPTS)

	def alive_timeout(self):
		self.sendall(Protocol.DISCONNECT)
		log.error("{} - Alive timeout, request to disconnect!".format(self.__class__.__name__))

	def check_still_alive(self):

		"""
		Scheduled to get called periodically (if still connected). Send ping to gateway.
		"""

		if not self.state_is("CONNECTED"):
			return

		self.sendall(Protocol.PING)
		self.queue.put((self.check_still_alive, next_check()))

		if (time.time() - self.timestamp) >= ALIVE_TIMEOUT:
			self.alive_timeout()

	def handle_init(self):

		"""	This is called just after a successful connection """

		if self.state_is("INIT"):
			self.sendall(Protocol.CONNECT)
		else:
			self.queue.put((self.check_still_alive, next_check()))

	def handle_ping(self):

		"""	Received a ping from gateway """

		self.timestamp = time.time()

	def handle_reroute(self, port):

		"""	Received a rerouting-request from gateway """

		self.host = (tcp_settings.address, port)
		self.set_state_to("REROUTING")

	def handle_reconnect(self):

		"""
		Called just after disconnected. Reschedule new attempt to connect (if
		allowed)
		"""

		if self.state_is("REROUTING"):
			return

		if self.reconnect() and self.set_state_to("RECONNECTING"):
			self.attempts += 1
			self.queue.put((self.start_service, next_reconnect()))
			kodi.notification("Connection lost - reconnecting... ({} of {})".format(self.attempts, MAX_ATTEMPTS))

		# blocking wait (polling loop, else XBMC/KODI locks during system shutdown)
		while not (self.event.wait(timeout=Events.POLL) or __monitor__.abortRequested()):
			pass

		self.event.clear()

	def state_connecting(self):

		# notify at the very beginning of the connection.
		if self.state_is("INIT"):
			tcp_settings.set_status(TCPIPSettings.STATUS, "Connecting...")

		self.set_state_to("CONNECTING")

	def state_connected(self):

		if self.set_state_to("CONNECTED"):
			tcp_settings.set_status(TCPIPSettings.STATUS, "Connected")

	def state_disconnected(self):

		if self.set_state_to("DISCONNECTED"):
			tcp_settings.set_status(TCPIPSettings.STATUS, "Disconnected")

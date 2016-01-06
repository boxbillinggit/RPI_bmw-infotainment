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
		self.current_state = state("INIT")

	def set_state(self, requested_state):
		pass


class Request(object):

	"""
	Current request from user.
	"""

	RUNNING, STOPPED = range(2)

	def __init__(self):
		self.current_request = Request.RUNNING


class Events(gateway_protocol.Protocol, tcp_socket.ThreadedSocket):

	"""
	Base class for handling all events regarding the TCP/IP-layer via a
	state-machine.
	"""

	# TODO: use acquire/release lock (notify, wait) instead of "event"??
	Event = threading.Event()
	POLL = 1

	def __init__(self, event=None, queue=None):
		gateway_protocol.Protocol.__init__(self)
		tcp_socket.ThreadedSocket.__init__(self)

		self.event = event or Events.Event
		self.queue = queue or event_handler.EventHandler.Queue

		self.host = tcp_settings.get_host()
		self.timestamp = time.time()
		self.attempts = 0

		states = States()
		self.state = states.current_state

		request = Request()
		self.request = request.current_request

	def state_is(self, trg_state):
		return self.state is States.state.index(trg_state)

	def start_service(self):

		"""
		Used to start -or restart service (from user -or event-handler).
		"""

		if self.request is Request.STOPPED:
			return

		if self.state_is("DISCONNECTED") or self.state_is("RECONNECTING"):
			self.state = state("INIT")
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

	def handle_init(self):

		"""
		This is called just after a successful connection.
		"""

		if self.state_is("INIT"):
			self.sendall(Protocol.CONNECT)
		else:
			self.queue.put((self.check_still_alive, next_check()))

	def alive_timeout(self):
		log.error("{} - Alive timeout!".format(self.__class__.__name__))
		self.sendall(Protocol.DISCONNECT)

	def check_still_alive(self):

		"""
		Scheduled to get called periodically (if still connected). Send ping to gateway.
		"""

		if self.state_is("CONNECTED"):
			self.sendall(Protocol.PING)
			self.queue.put((self.check_still_alive, next_check()))

			if (time.time() - self.timestamp) >= ALIVE_TIMEOUT:
				self.alive_timeout()

	def handle_ping(self):

		"""	Received a ping from gateway """

		self.timestamp = time.time()

	def handle_reroute(self, port):

		"""	Received a rerouting-request from gateway """

		self.state = state("REROUTING")
		self.host = (tcp_settings.address, port)

	def handle_reconnect(self):

		"""
		Called just after disconnected. Reschedule new attempt to connect (if
		allowed)
		"""

		if self.state_is("REROUTING"):
			return

		if self.state_is("RECONNECTING"):
			self.queue.put((self.start_service, next_reconnect()))

		# blocking wait (polling loop, else XBMC/KODI locks during system shutdown)
		while not (self.event.wait(timeout=Events.POLL) or __monitor__.abortRequested()):
			pass

		self.event.clear()

	def state_connecting(self):

		if self.state_is("INIT"):
			tcp_settings.set_status(TCPIPSettings.STATUS, "Connecting...")
		elif self.state_is("REROUTING"):
			self.state = state("CONNECTING")

	def state_connected(self):

		if self.state_is("INIT"):
			return

		self.state = state("CONNECTED")
		tcp_settings.set_status(TCPIPSettings.STATUS, "Connected")

	def state_disconnected(self):

		if self.state_is("REROUTING"):
			return

		if self.request is Request.RUNNING and (self.attempts < MAX_ATTEMPTS):
			self.attempts += 1
			self.state = state("RECONNECTING")
			kodi.notification("Disconnected. Reconnecting... (no. {})".format(self.attempts))
		else:
			self.attempts = 0
			self.state = state("DISCONNECTED")

		tcp_settings.set_status(TCPIPSettings.STATUS, "Disconnected")

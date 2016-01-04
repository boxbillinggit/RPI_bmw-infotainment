import time
import threading

import kodi
import gateway_protocol
import event_handler
import log as log_module

log = log_module.init_logger(__name__)
TCPIPSettings = kodi.TCPIPSettings
Protocol = gateway_protocol.Protocol

__author__ = 'lars'

ALIVE_TIMEOUT = 10
RECONNECT = 15
MAX_ATTEMPTS = 5


def state(string):
	return State.state.index(string)


def next_alivetimeout_check():
	return time.time() + Events.PING_TIME_INTERVAL


def next_reconnect():
	return time.time() + RECONNECT

# TODO: fix this:
class Settings(object):

	"""
	Storage class containing the current requested port -and ip-address.
	"""

	def __init__(self, host):
		self.host = host
		self.address = host[0]
		self.port = host[1]


class State(object):

	"""
	Storage class State for current TCP-connection.
	"""

	state = ["INIT", "REROUTING", "CONNECTING", "CONNECTED", "DISCONNECTED", "RECONNECTING"]

	def __init__(self):
		self.current_state = state("INIT")


tcp_settings = kodi.TCPIPSettings()


class Events(Protocol):

	"""
	Base class for handling events from gateway-protocol (ping, reroute, etc),
	TCP/IP-socket and also module's interface (send, recive, start, stop)

	State-machine for managing connections. Also works as a proxy-
	interface for managing all function handling between send/receive/start/stop

	"""

	# TODO: use notify instead of event??
	Event = threading.Event()

	PING_TIME_INTERVAL = 3
	TIME_RECONNECT = 10

	def __init__(self, event=None, queue=None):
		super(Events, self).__init__()
		self.event = event or Events.Event
		self.queue = queue or event_handler.EventHandler.Queue
		self.settings = Settings(tcp_settings.get_host())
		self.host = self.settings.host
		self.timestamp = time.time()
		self.attempts = 0
		self.forced = False

		state = State()
		self.state = state.current_state

	def request_start(self):

		"""
		Used to start -or restart service (from user -or event-handler).
		"""

		if self.state is state("DISCONNECTED") or self.state is state("RECONNECTING"):
			self.state = state("INIT")
			self.host = tcp_settings.get_host()

			self.forced = False
			self.timestamp = time.time()
			self.event.set()

	def request_stop(self):

		"""
		Request from GUI to disconnect. Send a disconnect request to gateway
		and the server will disconnect us gracefully.
		"""

		# TODO: abort state "RECONNECT"

		if self.state is state("CONNECTED"):
			self.forced = True
			self.sendall(Protocol.DISCONNECT)
		else:
			print "DEBUG - not connected... (close socket?)"

	def handle_init(self):

		"""
		This is called just after a successful connection.
		"""

		if self.state is state("INIT"):
			self.sendall(Protocol.CONNECT)
		else:
			self.queue.put((self.check_still_alive, next_alivetimeout_check()))

	def alive_timeout(self):
		log.debug("class {} - Alive timeout, disconnecting".format(self.__class__.__name__))
		self.sendall(Protocol.DISCONNECT)

	def check_still_alive(self):

		"""
		Scheduled each PING_INTERVAL to check if we're still alive
		then transmit ping. else close connection with alive_timeout()
		"""

		if self.state is state("CONNECTED"):
			self.sendall(Protocol.PING)
			self.queue.put((self.check_still_alive, next_alivetimeout_check()))

			if time.time()-self.timestamp >= ALIVE_TIMEOUT:
				self.alive_timeout()

	def handle_ping(self):

		"""
		Called from class Protocol (within thread)
		"""

		self.timestamp = time.time()

	def handle_reroute(self, port):

		"""
		Called from class Protocol (but from within thread)

		We have not disconnected the socket at this state.. just update port to
		connect against until next connection.
		"""

		self.state = state("REROUTING")
		self.host = (self.settings.address, port)

	def handle_reconnect(self):

		"""
		Called just after disconnected (from class ThreadedSocket)

		reschedule new attempt to connect if we didn't force a disconnection.
		"""

		if self.state is state("RECONNECTING"):
			self.queue.put((self.request_start, next_reconnect()))

		if self.state is not state("REROUTING"):
			# TODO: prevents KODI from shutdown
			self.event.wait()
			self.event.clear()

	def state_connecting(self):
		if self.state is state("INIT"):
			tcp_settings.set_status(TCPIPSettings.STATUS, "Connecting...")

	def state_connected(self):
		if self.state is not state("INIT"):
			self.state = state("CONNECTED")
			tcp_settings.set_status(TCPIPSettings.STATUS, "Connected")

	def state_disconnected(self):
		if self.state is not state("REROUTING"):

			tcp_settings.set_status(TCPIPSettings.STATUS, "Disconnected")

			if self.attempts < MAX_ATTEMPTS and not self.forced:
				tcp_settings.notify_disconnected("Disconnected (no. {}) reconnecting... ".format(self.attempts))
				self.attempts += 1
				self.state = state("RECONNECTING")
			else:
				self.attempts = 0
				self.state = state("DISCONNECTED")

	def sendall(self, data):
		"""
		Overridden in subclass
		"""
		pass

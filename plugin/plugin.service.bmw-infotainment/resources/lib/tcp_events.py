import time
import threading

import kodi
import statemachine
import settings
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
addon_settings = kodi.AddonSettings()

__author__		= 'lars'
__monitor__ 	= xbmc.Monitor()


class State(statemachine.State):

	"""
	Current state on TCP-connection.
	"""

	states = ("INIT", "REROUTING", "CONNECTING", "CONNECTED", "DISCONNECTED", "RECONNECTING")

	INIT, REROUTING, CONNECTING, CONNECTED, DISCONNECTED, RECONNECTING = range(6)

	def __init__(self):
		super(State, self).__init__(State.INIT)

		self.transitions = \
			{"from": (State.INIT,),         "to": (State.REROUTING, State.DISCONNECTED)}, \
			{"from": (State.REROUTING,),    "to": (State.CONNECTING,)}, \
			{"from": (State.CONNECTING,),   "to": (State.CONNECTED, State.DISCONNECTED)}, \
			{"from": (State.CONNECTED,),    "to": (State.DISCONNECTED,)}, \
			{"from": (State.DISCONNECTED,), "to": (State.RECONNECTING, State.INIT)}, \
			{"from": (State.RECONNECTING,), "to": (State.INIT,)}


class Request(object):

	"""
	Current request from user.
	"""

	RUNNING, STOPPED = range(2)

	def __init__(self):
		self.current_request = Request.RUNNING


class Events(gateway_protocol.Protocol, tcp_socket.ThreadedSocket, State):

	"""
	Base class for handling all events for the TCP/IP-layer with help from a
	state-machine.
	"""

	Event = threading.Event()
	POLL = 1

	@staticmethod
	def next_reconnect():
		return time.time() + settings.TCPIP.TIME_RECONNECT

	def __init__(self, event=None):
		State.__init__(self)
		gateway_protocol.Protocol.__init__(self)
		tcp_socket.ThreadedSocket.__init__(self)

		self.event = event or Events.Event

		self.host = addon_settings.get_host()
		self.timestamp = time.time()
		self.attempts = 0
		self.send_buffer = ""

		request = Request()
		self.request = request.current_request

	def start_service(self):

		"""
		Used to start -or restart service (from user -or internally by event-handler).
		"""

		if self.request is Request.STOPPED:
			return

		if self.set_state_to(State.INIT):
			self.host = addon_settings.get_host()
			self.timestamp = time.time()
			self.event.set()

	def stop_service(self):

		"""
		Request from user to disconnect. Broadcast disconnect to gateway
		and the server will disconnect us gracefully.
		"""

		if self.state_is(State.CONNECTED):
			self.sendall(Protocol.DISCONNECT)

	def handle_send(self, data):

		"""
		Method for sending data. we must be connected, else buffer data and send
		when connected.
		"""

		# TODO: how to handle send? is it blocking long time, etc.. run in a separate thread??

		if self.state_is(State.CONNECTED):
			self.sendall(data)
		else:
			self.send_buffer += data

	def send_data_buffered(self):

		"""	Send data accumulated when DISCONNECTED """

		if self.send_buffer:
			self.sendall(self.send_buffer)
			del self.send_buffer[:]

	def reset_attempts(self):

		"""	Called only when user requests to connect """

		self.attempts = 0

	def allowed_to_reconnect(self):

		"""	Are we allowed to reconnect (after a unintended disconnection)? """

		return self.request is Request.RUNNING and (self.attempts < settings.TCPIP.MAX_ATTEMPTS)

	def alive_timeout(self):

		"""	We have not received a ping lately.. """

		# TODO how to handle, is pipe broken??
		# self.set_state_to(State.DISCONNECTED)
		log.error("{} - Alive timeout! Is pipe broken???".format(self.__class__.__name__))

	def check_still_alive(self):

		"""
		Scheduled to get called periodically, as long as method returns "True" (while
		still connected). Send a ping to the gateway.
		"""

		if not self.state_is(State.CONNECTED):
			return

		self.sendall(Protocol.PING)

		if (time.time() - self.timestamp) >= settings.TCPIP.ALIVE_TIMEOUT:
			self.alive_timeout()

		return True

	def handle_init(self):

		"""	This is called just after a successful connection """

		if self.state_is(State.INIT):
			self.sendall(Protocol.CONNECT)
		else:
			next_check = time.time() + settings.TCPIP.TIME_INTERVAL_PING
			event_handler.add(self.check_still_alive, timestamp=next_check, interval=settings.TCPIP.TIME_INTERVAL_PING)

	def handle_ping(self):

		"""	Received a ping from gateway """

		self.timestamp = time.time()

	def handle_reroute(self, port):

		"""	Received a rerouting-request from gateway """

		self.host = (addon_settings.address, port)
		self.set_state_to(State.REROUTING)

	def handle_reconnect(self):

		"""
		Called just after a disconnection. Reschedule new attempt to connect (if
		allowed). This method blocks until event is set. Using a polling loop, else
		XBMC/KODI locks during system shutdown.
		"""

		if self.state_is(State.REROUTING):
			return

		if self.allowed_to_reconnect() and self.set_state_to(State.RECONNECTING):
			self.attempts += 1
			event_handler.add(self.start_service, timestamp=Events.next_reconnect())
			kodi.notify_disconnected(self.attempts)

		while not (self.event.wait(timeout=Events.POLL) or __monitor__.abortRequested()):
			pass

		self.event.clear()

	def state_connecting(self):

		"""
		Set status connecting in the very beginning of the connection.
		"""

		if self.state_is(State.INIT):
			addon_settings.set_status(self.translate_state(State.CONNECTING))

		self.set_state_to(State.CONNECTING)

	def state_connected(self):

		"""
		Successfully connected, Empty the send-buffer
		"""

		if self.set_state_to(State.CONNECTED):
			addon_settings.set_status(self.translate_state())
			self.send_data_buffered()

	def state_disconnected(self):

		"""
		Socket is disconnected.
		"""

		if self.set_state_to(State.DISCONNECTED):
			addon_settings.set_status(self.translate_state())

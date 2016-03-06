import time
import threading
import settings
import event_handler
import log as log_module

from statemachine import StateMachine
from kodi import __addonid__, __xbmcgui__, addon_settings
from kodi.callbacks import GUI, UPDATE_STATUS
from gateway_protocol import Protocol
from tcp_socket import ThreadedSocket

log = log_module.init_logger(__name__)

__author__ = 'lars'

ADDRESS, PORT = range(2)


class State(StateMachine):

	"""
	Current state on TCP-connection.
	"""

	states = ("INIT", "REROUTING", "CONNECTING", "CONNECTED", "DISCONNECTED", "RECONNECTING")

	INIT, REROUTING, CONNECTING, CONNECTED, DISCONNECTED, RECONNECTING = range(6)

	CurrentState = INIT

	def __init__(self):
		super(State, self).__init__(State.INIT, State.new_state)

		self.transitions = \
			{"from": (State.INIT,),         "to": (State.REROUTING, State.DISCONNECTED)}, \
			{"from": (State.REROUTING,),    "to": (State.CONNECTING,)}, \
			{"from": (State.CONNECTING,),   "to": (State.CONNECTED, State.DISCONNECTED)}, \
			{"from": (State.CONNECTED,),    "to": (State.DISCONNECTED,)}, \
			{"from": (State.DISCONNECTED,), "to": (State.RECONNECTING, State.INIT)}, \
			{"from": (State.RECONNECTING,), "to": (State.INIT,)}

	@classmethod
	def new_state(cls, new_state):

		""" update static class-variable for current state on TCP connection """

		cls.CurrentState = new_state


class Request(object):

	"""
	Current request from user.
	"""

	RUNNING, STOPPED = range(2)

	def __init__(self):
		self.current_request = Request.RUNNING


class Events(Protocol, ThreadedSocket, State):

	"""
	Base class for handling all events for the TCP/IP-layer with help from a
	state-machine.
	"""

	Event = threading.Event()
	POLL = 1

	@staticmethod
	def next_reconnect():
		return time.time() + settings.TCPIP.TIME_RECONNECT

	def __init__(self, condition=None, event=None):
		State.__init__(self)
		Protocol.__init__(self)
		ThreadedSocket.__init__(self, condition)

		self.event = event or Events.Event

		self.host = addon_settings.get_host()
		self.timestamp = time.time()
		self.attempts = 0
		self.send_buffer = []

		request = Request()
		self.request = request.current_request

	def _request_connect(self):

		"""
		Used to connect -or reconnect (from user -or internally by event-handler).
		"""

		if self.request is Request.STOPPED:
			return

		if self.set_state_to(State.INIT):
			self.host = addon_settings.get_host()
			self.timestamp = time.time()
			self.event.set()

	def _request_disconnect(self):

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

		if self.state_is(State.CONNECTED):
			self.sendall(data)
		else:
			self.send_buffer.append(data)

	def send_data_buffered(self):

		"""	Send data accumulated when DISCONNECTED """

		for chunk in self.send_buffer:
			self.sendall(chunk)

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

	def notify_disconnected(self):

		""" Notify user, but only if an unintended disconnection occurred (not triggered by user) """

		msg = "Connection lost, reconnecting... ({} of {})".format(self.attempts, settings.TCPIP.MAX_ATTEMPTS)
		__xbmcgui__.Dialog().notification(__addonid__, msg)

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

		self.host = (self.host[ADDRESS], port)
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
			self.notify_disconnected()
			event_handler.add(self._request_connect, timestamp=Events.next_reconnect())

		while not (self.event.wait(timeout=Events.POLL) or not self.still_alive()):
			pass

		self.event.clear()

	def state_connecting(self):

		"""
		Set status connecting in the very beginning of the connection.
		"""

		if self.state_is(State.INIT):
			GUI.event(UPDATE_STATUS, self.translate_state(State.CONNECTING))

		self.set_state_to(State.CONNECTING)

	def state_connected(self):

		"""
		Successfully connected, Empty the send-buffer (not from current ThreadedSocket
		but from EventHandler-thread)
		"""

		if self.set_state_to(State.CONNECTED):
			GUI.event(UPDATE_STATUS, self.translate_state())
			event_handler.add(self.send_data_buffered)

	def state_disconnected(self):

		"""
		Socket is disconnected.
		"""

		if self.set_state_to(State.DISCONNECTED):
			GUI.event(UPDATE_STATUS, self.translate_state())

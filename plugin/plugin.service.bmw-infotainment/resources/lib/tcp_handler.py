"""
This is the current main TCP-interface.
"""
import time
import event_handler
import signaldb
import gateway_protocol
import log as log_module

from kodi.callbacks import GUI, Application, UPDATE_STATS
from tcp_events import Events, Request
from signal_handler import SignalHandler

__author__ = 'lars'

log = log_module.init_logger(__name__)


class BusStats(object):

	"""
	Calculating bus activity, always good to know when tampering with the LIN-bus.
	Each tcp-frame has an overhead, subtract these from bytes handled.

	BaudRate - bits/second

	Ref: https://learn.sparkfun.com/tutorials/serial-communication/rules-of-serial
	"""

	TCP_OVERHEAD = 4
	UPDATE_RATE = 5

	def __init__(self):
		baudrate = int(signaldb.get_setting("BaudRate"))
		databits = int(signaldb.get_setting("DataBits"))
		stopbits = int(signaldb.get_setting("StopBits"))

		# include parity and start-bit = 2
		self.max_rate = baudrate / (databits + stopbits + 2)
		self.timestamp = time.time()
		self.bytes = 0

		self.start()

	def start(self):
		event_handler.add(self.update_value, interval=BusStats.UPDATE_RATE)

	def add_bytes(self, bytes_handled):
		self.bytes += bytes_handled - BusStats.TCP_OVERHEAD

	def update_value(self):

		""" Updates bus-activity periodically """

		percent = self.bytes / ((time.time() - self.timestamp) * self.max_rate)
		GUI.event(UPDATE_STATS, percent)
		log.debug("Current bus-activity: {:.2%}".format(percent))

		self.bytes = 0
		self.timestamp = time.time()

		# reschedule (periodic task)
		return True


class TCPIPHandler(Events):

	"""
	Main interface for all TCP/IP-handling.
	"""

	def __init__(self, condition=None):
		super(TCPIPHandler, self).__init__(condition)
		self.signal_handler = SignalHandler(self.send)
		self.bus_stats = BusStats()
		self._bind_callbacks()

	def _bind_callbacks(self):

		"""
		Set callbacks, triggered from GUI.
		"""

		Application.Callbacks.update(onConnect=self.request_connect)
		Application.Callbacks.update(onDisconnect=self.request_disconnect)

	def request_connect(self):

		"""
		User calls this method for connecting.
		"""

		self.request = Request.RUNNING
		self.reset_attempts()
		self._request_connect()

	def request_disconnect(self):

		"""
		User calls this method for disconnecting (also system shutdown).
		"""

		self.request = Request.STOPPED
		self._request_disconnect()

	def send(self, signal):

		"""
		Interface against other modules to send data through TCP/IP-socket.

		"signal" is 3-tuple hexstring: ("src", "dst", "data")
		"""

		data = gateway_protocol.create_frame(signal)

		self.handle_send(data)
		self.bus_stats.add_bytes(len(data))

	def receive(self, data):

		"""
		Interface against other modules to receive data from TCP/IP-socket (callback
		from ThreadedSocket). Handles the raw bytes received from the socket and
		abstracts the overlaying TCP/IP-protocol away allowing only signals passing
		through to the signal "filter".

		"signal" is 3-tuple hexstring: ("src", "dst", "data")
		"""

		raw_signals = self.handle_receive(bytearray(data))

		for data in raw_signals:
			self.signal_handler.receive(gateway_protocol.create_signal(data))
			self.bus_stats.add_bytes(len(data))

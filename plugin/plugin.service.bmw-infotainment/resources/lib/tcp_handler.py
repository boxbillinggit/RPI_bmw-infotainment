"""
This is the current main TCP-interface to use.
"""

import kodi
import time
import signaldb
import gateway_protocol
import signal_handler
import tcp_events

from event_handler import Scheduler

__author__ = 'lars'

Request = tcp_events.Request


class BusStats(object):

	"""
	Calculating bus activity, always good to know when tampering with the lin-bus.
	Each tcp-frame has an overhead, subtract these from bytes handled.

	BaudRate - bits/second

	Ref: https://learn.sparkfun.com/tutorials/serial-communication/rules-of-serial
	"""

	TCP_OVERHEAD = 5
	UPDATE_RATE = 5

	def __init__(self):
		baudrate = int(signaldb.get_setting("BaudRate"))
		databits = int(signaldb.get_setting("DataBits"))
		stopbits = int(signaldb.get_setting("StopBits"))

		# include parity and start-bit = 2
		self.max_rate = baudrate / (databits + stopbits + 2)
		self.timestamp = time.time()
		self.bytes = 0

		self.scheduler = Scheduler()
		self.start()

	def start(self):
		self.scheduler.add(self.update_value, interval=BusStats.UPDATE_RATE)

	def add_bytes(self, bytes):
		self.bytes += bytes - BusStats.TCP_OVERHEAD

	def update_value(self):

		current_rate = self.bytes / (time.time() - self.timestamp)
		kodi.AddonSettings.set_bus_activity(current_rate/self.max_rate)

		self.bytes = 0
		self.timestamp = time.time()

		# reschedule (periodic task)
		return True


class TCPIPHandler(tcp_events.Events):

	"""
	Main interface for all TCP/IP-handling.
	"""

	def __init__(self):
		super(TCPIPHandler, self).__init__()
		self.filter = signal_handler.Filter()
		self.bus_stats = BusStats()

	def request_start(self):

		"""
		User calls this method for connecting.
		"""

		self.request = Request.RUNNING
		self.reset_attempts()
		self.start_service()

	def request_stop(self):

		"""
		User calls this method for disconnecting (also system shutdown).
		"""

		self.request = Request.STOPPED
		self.stop_service()

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
			self.filter.handle_signal(gateway_protocol.create_signal(data))
			self.bus_stats.add_bytes(len(data))

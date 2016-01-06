"""
This is the current main TCP-interface to use.
"""

import gateway_protocol
import signal_handler
import tcp_events

__author__ = 'lars'

Request = tcp_events.Request


class TCPIPHandler(tcp_events.Events):

	"""
	Main interface for all TCP/IP-handling.
	"""

	def __init__(self):
		super(TCPIPHandler, self).__init__()
		self.filter = signal_handler.Filter()

	def request_start(self):

		"""
		User calls this method for connecting.
		"""

		self.request = Request.RUNNING
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

		"signal" is 3-tuple: ([src], [dst], [data])
		"""

		self.sendall(gateway_protocol.create_frame(signal))

	def receive(self, data):

		"""
		Interface against other modules to receive data from TCP/IP-socket (callback
		from ThreadedSocket). Handles the raw bytes received from the socket and
		abstracts the overlaying TCP/IP-protocol away allowing only signals passing
		through to the signal "filter".

		"signal" is 3-tuple: ([src], [dst], [data])
		"""

		signals = self.handle_data(bytearray(data))

		for signal in signals:
			self.filter.handle_signal(signal)

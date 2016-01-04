"""
This is the current main TCP-interface to use.
"""

import gateway_protocol
import signal_handler
import tcp_socket

__author__ = 'lars'


class TCPIPHandler(tcp_socket.ThreadedSocket):

	"""
	Main interface for all TCP/IP-handling. Support handling for sending and receiving
	signals, also stopping and starting TCP/IP-service.
	"""

	def __init__(self):
		super(TCPIPHandler, self).__init__()
		self.filter = signal_handler.Filter()

	def start_service(self):

		"""
		Use this method for starting the service.
		"""

		self.request_start()

	def stop_service(self):

		"""
		Use this method for stopping the service.
		"""

		self.request_stop()

	def send(self, signal):

		"""
		Method to use for sending data to TCP/IP-socket.

		signal is 3-tuple: ([src], [dst], [data])
		"""

		self.sendall(gateway_protocol.create_frame(signal))

	def receive(self, data):

		"""
		Callback from ThreadedSocket. Handles the raw bytes received from the socket.
		Passes through data from the bus to signal-handler and abstracts the overlay
		TCP/IP-protocol away.

		signal is 3-tuple: ([src], [dst], [data])
		"""

		signals = self.handle_data(bytearray(data))

		for signal in signals:
			self.filter.handle_signal(signal)

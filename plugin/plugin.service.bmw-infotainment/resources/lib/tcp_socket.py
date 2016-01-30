"""
Implements the TCP-socket transport layer.
"""
import socket
import threading
import log as log_module

log = log_module.init_logger(__name__)

__author__ = 'lars'


def default_condition():

	""" Default condition for running thread (TODO create Threading.condition)"""

	return True


class ThreadedSocket(threading.Thread):

	"""
	TCP/IP-socket running in a separate thread.
	"""

	MAX_RECV = 1024

	def __init__(self, condition=None):
		super(ThreadedSocket, self).__init__()
		self.still_alive = condition or default_condition
		self.name = "ThreadedSocket"
		self.daemon = True

		self.sockfd = None
		self.host = None

	def run(self):

		"""
		Thread's main activity - main loop for the state machine.
		"""

		while self.still_alive():

			if self.connect():
				self.handle_init()
				self.recv()
			self.state_disconnected()
			self.handle_reconnect()

	def connect(self):

		"""
		Create a connection and return "True" if succeeded
		"""

		self.state_connecting()

		try:
			sockfd = socket.create_connection(self.host)

		except (socket.error, socket.timeout) as error:
			log.error("{} - failed to connect: {}".format(self.__class__.__name__, error))
			return

		self.sockfd = sockfd
		self.state_connected()

		return True

	def recv(self):

		"""
		Mainloop for receiving data from TCP/IP-socket.
		"""

		while self.still_alive():

			try:
				data = self.sockfd.recv(ThreadedSocket.MAX_RECV)
			except socket.error:
				break

			if not data:
				break

			self.receive(data)

		self.sockfd.close()

	def sendall(self, data):

		"""
		Method for sending data to TCP/IP-socket.
		"""

		if not self.sockfd:
			return

		try:
			self.sockfd.sendall(data)
		except socket.error as error:
			log.error("{} - failed to send data on socket: {}".format(self.__class__.__name__, error))

	def state_connecting(self):
		""" Overridden in subclass """
		pass

	def state_connected(self):
		""" Overridden in subclass """
		pass

	def handle_init(self):
		""" Overridden in subclass """
		pass

	def receive(self, data):
		""" Overridden in subclass """
		pass

	def state_disconnected(self):
		""" Overridden in subclass """
		pass

	def handle_reconnect(self):
		""" Overridden in subclass """
		return False

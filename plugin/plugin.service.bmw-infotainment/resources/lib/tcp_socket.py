"""
Implements the TCP-socket. Events are inherited from Events-class
"""

import socket
import threading

try:
	import xbmc
except ImportError:
	import resources.lib.debug.xbmc as xbmc

import tcp_events
import log as log_module
log = log_module.init_logger(__name__)

__author__		= 'lars'
__monitor__ 	= xbmc.Monitor()


class ThreadedSocket(threading.Thread, tcp_events.Events):

	"""
	TCP/IP-socket running in a separate thread.
	"""

	TIMEOUT = 10
	MAX_RECV = 1024

	def __init__(self):
		super(ThreadedSocket, self).__init__()
		tcp_events.Events.__init__(self)
		self.daemon = True
		self.sockfd = None

	def run(self):

		"""
		Thread's main activity - main loop for the state machine.
		"""

		while not __monitor__.abortRequested():

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
			# sockfd = socket.create_connection(self.host, ThreadedSocket.TIMEOUT)
			sockfd = socket.create_connection(self.host)

		except (socket.error, socket.timeout) as error:
			log.debug("{} - failed to connect: {}".format(self.__class__.__name__, error))
			return

		self.sockfd = sockfd
		self.state_connected()

		return True

	def recv(self):

		"""
		Mainloop for receiving data from TCP/IP-socket.
		"""

		while not __monitor__.abortRequested():

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
			self.sockfd.sendall(bytearray(data))
		except socket.error as error:
			log.debug("{} - failed to send data on socket: {}".format(self.__class__.__name__, error))

	def receive(self, data):
		"""
		called when data is received on TCP/IP-socket.

		Overridden in subclass.
		"""
		pass

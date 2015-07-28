"""
This module handles the actual TCP/IP transportation on socket. two options is available (asyncore loop -or native socket)
"""

import log as logger
log = logger.init_logger(__name__)

try:
	import xbmc, xbmcplugin, xbmcgui, xbmcaddon

except ImportError as err:
	log.warning("%s - using 'debug.XBMC'-modules instead" % err.message)
	import debug.XBMC as xbmc
	import debug.XBMCGUI as xbmcgui
	import debug.XBMCADDON as xbmcaddon

__author__ 		= 'Lars'
__monitor__ 	= xbmc.Monitor()
__addon__		= xbmcaddon.Addon()
__addonname__	= __addon__.getAddonInfo('name')
__addonid__		= __addon__.getAddonInfo('id')

import asyncore
import socket
import errno
from threading import Thread

# settings for TCP transport
MAX_RECVBUFFER = 512


# print a well formed HEX-string from a 'bytearray'
def to_hexstr(bytearray):
	return " ".join(map(lambda byte: "%X" % byte, bytearray))


class TCPIPSocketAsyncore(asyncore.dispatcher):

	def __init__(self):

		# init variables (TODO: one buffer for each socket?)
		self.tx_buffer = bytearray()
		self.rx_buffer = bytearray()

		# TODO: which socket we're interested in (in this case only one, but anyway..
		self.map_selector = None

		# inherited from 'asyncore.dispatcher'
		self.connected = False
		self.connecting = False

		# init dispatcher class
		asyncore.dispatcher.__init__(self)

	def start(self):

		# update status in "settings"
		__addon__.setSetting("gateway.status", "Connecting...")

		# blocking until disconnected.. loop through all channels in 'map' each 0.1s
		asyncore.loop(0.1)


	# TODO: need to be called within the loop (need to select socket)
	def is_connected(self):

		return self.connected or self.connecting

	def reroute_connection(self, host, port):

		log.debug("%s - rerouting to port [%s] ..." % (self.__class__.__name__, port))

		# adds a channel (connect a socket)
		self.create_socket(socket.AF_INET, socket.SOCK_STREAM)
		self.connect( (host, port) )

	# overrides method in asynchore.dispatcher
	def handle_connect(self):
		log.debug("%s - Socket opened [file-no:%s name:%s]" % (self.__class__.__name__, self.socket.fileno(), self.socket.getsockname()))

		# update status in "settings"
		__addon__.setSetting("gateway.status", "Connected")

	def handle_close(self):
		log.debug("%s - Socket closed [file-no:%s name:%s]" % (self.__class__.__name__, self.socket.fileno(), self.socket.getsockname()))

		# update status in "settings"
		__addon__.setSetting("gateway.status", "Disconnected")

		# call in class 'dispatcher'
		self.close()

	def handle_read(self):

		# fill buffer with more frames
		self.rx_buffer += bytearray(self.recv(MAX_RECVBUFFER))

		# DEBUG
		log.debug("%s - handle_read - [%s]" % (self.__class__.__name__, to_hexstr(self.rx_buffer)))

		self.handle_message()



	def writable(self):

		# if we're have something to write. then wait for next poll loop (30 seconds default, not good)
		return (not self.connected) or len(self.tx_buffer)

	# TODO: how are we selecting socket to send to??
	def handle_write(self):
		if self.tx_buffer:
			sent = self.send(self.tx_buffer)
			log.debug("%s - sending chunk: [%s] (bytes sent:%s)" % (self.__class__.__name__, to_hexstr(self.tx_buffer), sent))
			self.tx_buffer = self.tx_buffer[sent:]

		else:
			pass

	# this will be overridden in inherited class
	# TODO: rename to 'rx_tcp_ip_frame'??
	def handle_message(self):
		pass

	# linearization with class methods in 'TCPDaemonNative' (dummy function does nothing but fill buffer).
	def send_buffer(self, buf):
		self.tx_buffer += bytearray(buf)

# use native sockets instead
# TODO: not in use... fix this!
class TCPIPSocketNative:

	def __init__(self):

		# init variables
		self.tx_buffer = None
		self.rx_buffer = None

		# status
		self.connected = False
		#self.connecting = False

		# init socket objects
		self.socket = None

		# DEBUG
		xbmc.log("BMW: init 'TCPDaemonNative' class done!", xbmc.LOGDEBUG)

	def launch_tcp_socket(self):

		# update status in "settings"
		__addon__.setSetting("gateway.status", "Connecting...")

		#update status flag
		self.connecting = True

		xbmc.log("BMW: launching TCP daemon. (start asyncore loop)", xbmc.LOGDEBUG)

		# blocking until disconnected..
		#asyncore.loop()

		xbmc.log("BMW: stopped TCP daemon. (exit asyncore loop)", xbmc.LOGDEBUG)

	def is_connected(self):

		xbmc.log("BMW: are we connected [%s] or connecting [%s] " % (self.connected,  self.connecting), xbmc.LOGDEBUG)
		return (self.connected or self.connecting)

	def reroute_connection(self, host, port):

		xbmc.log("BMW: rerouting to port %s ..." % port, xbmc.LOGDEBUG)

		try:
			# create the socket object -and connect.
			self.socket = socket.create_connection((host, port))

		except socket.error as err:
			if err.errno == errno.ECONNREFUSED:

				# error log
				xbmc.log("Connection refused (no port available on host)", xbmc.LOGERROR)
			else:
				xbmc.log("some other error: %s" % err.strerror, xbmc.LOGERROR)

			return False

		self.connected = True
		self.tcp_daemon = Thread(name='TCP-daemon', target=self.tcp_daemon_listener)
		#self.tcp_daemon.daemon = True
		self.tcp_daemon.start()

		# succeeded to connect?
		return True

	# thread for socket listener
	def tcp_daemon_listener(self):

		# loop until not connected anymore
		while self.connected:

			# convert from 'str' to 'bytearray'
			self.rx_buffer = bytearray(self.socket.recv(MAX_RECVBUFFER))

			# handle closed connections here?
			if self.tx_buffer:

				# function call in base class
				self.handle_message(self.tx_buffer)

			# request close from OpenBM-daemon
			else:
				# close socket
				self.handle_close()


	# NOT in use
	# almost (not exactly) same method as in Asynchore
	def handle_read(self):

		# convert from 'str' to 'bytearray'
		self.rx_buffer = bytearray(self.rx_buffer)
		self.handle_message(self.rx_buffer)

	# handles the closnig of socket
	def handle_close(self):

		# log
		xbmc.log("BMW: Socket closed... (%s %s)" % (self.socket.fileno(), self.socket.getsockname()), xbmc.LOGDEBUG)

		# update status in "settings"
		__addon__.setSetting("gateway.status", "Disconnected")

		self.connected = False
		self.socket.close()


	# send bytes
	def send_buffer(self):

		try:
			# send buffer
			tx = self.socket.send(self.tx_buffer)

			# clear buffer
			self.tx_buffer = self.tx_buffer[tx:]

		except socket.err as err:
			xbmc.log("BMW: error during send: %s (%s %s)" % (err.strerror, self.socket.fileno(), self.socket.getsockname()), xbmc.LOGERROR)

			# TODO: call handle_close here?
			self.handle_close()

	# overriden in class inheritance
	def handle_message(self, rx):
		pass
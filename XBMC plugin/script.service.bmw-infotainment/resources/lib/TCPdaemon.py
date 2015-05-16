__author__ = 'Lars'

# Python dev docs: http://mirrors.kodi.tv/docs/python-docs/14.x-helix/
import xbmc, xbmcplugin, xbmcgui, xbmcaddon

import asyncore, socket, errno
from threading import Thread

__addon__		= xbmcaddon.Addon()
__addonname__	= __addon__.getAddonInfo('name')


# handles the actual transportation of TCP messages (rx and tx).
# with asyncore -or native socket.


class TCPDaemonAsyncore(asyncore.dispatcher):

	# settings for TCP transport
	MAX_RECVBUFFER = 512

	def __init__(self):

		# init variables (TODO: one buffer for each socket?)
		self.tx_buffer = None
		self.rx_buffer = None

		# TODO: which socket we're interested in (in this case only one, but anyway..
		self.map_selector = None

		# inherited from 'asyncore.dispatcher'
		#self.connected = False
		#self.connecting = False

		# init dispatcher class
		asyncore.dispatcher.__init__(self)

		# DEBUG
		xbmc.log("BMW: init 'TCPDaemonAsyncore' class done!", xbmc.LOGDEBUG)

	def launch_tcp_daemon(self):

		# update status in "settings"
		__addon__.setSetting("gateway.status", "Connecting...")

		xbmc.log("BMW: launching TCP daemon. (start asyncore loop)", xbmc.LOGDEBUG)

		# blocking until disconnected.. loop through all channels in 'map' each 0.1s
		# TODO understand this loop-thing
		asyncore.loop(0.1)

		xbmc.log("BMW: connection lost. (exit asyncore loop)", xbmc.LOGINFO)

	#TODO need to be called within the loop (need to select socket)
	def is_connected(self):

		xbmc.log("BMW: are we connected [%s] or connecting [%s] " % (self.connected,  self.connecting), xbmc.LOGDEBUG)
		return (self.connected or self.connecting)

	def reroute_connection(self, host, port):

		xbmc.log("BMW: rerouting to port %s ..." % port, xbmc.LOGDEBUG)

		# adds a channel (connect a socket)
		self.create_socket(socket.AF_INET, socket.SOCK_STREAM)
		self.connect( (host, port) )


	def handle_connect(self):
		xbmc.log("BMW: Socket opened... (%s %s)" % (self.socket.fileno(), self.socket.getsockname()), xbmc.LOGDEBUG)

		# update status in "settings"
		__addon__.setSetting("gateway.status", "Connected")

	def handle_close(self):
		#generates error.
		#xbmc.log("BMW: Socket closed... (%s %s)" % (self.socket.fileno(), self.socket.getsockname()), xbmc.LOGDEBUG)

		xbmc.log("BMW: Socket closed...", xbmc.LOGDEBUG)

		# update status in "settings"
		__addon__.setSetting("gateway.status", "Disconnected")

		# call in class 'dispatcher'
		self.close()

	def handle_read(self):

		# convert from 'str' to 'bytearray'
		self.rx_buffer = bytearray(self.recv(self.MAX_RECVBUFFER))

		# log
		#xbmc.log("BMW: handle_read(): %s (%s %s)" % (str(self.rx_buffer).encode('hex'), self.socket.fileno(), self.socket.getsockname()), xbmc.LOGDEBUG)
		xbmc.log("BMW: handle_read(): %s" % str(self.rx_buffer).encode('hex'), xbmc.LOGDEBUG)

		self.handle_message(self.rx_buffer)



	def writable(self):

		# if we're have something to write. then wait for next poll loop (30 seconds default, not good)
		return (not self.connected) or len(self.tx_buffer)

	# TODO: how are we selecting socket to send to??
	def handle_write(self):
		if self.tx_buffer:
			sent = self.send(bytearray(self.tx_buffer))
			self.tx_buffer = self.tx_buffer[sent:]
			#xbmc.log("BMW: handle_write(): %s (%s %s)" % (str(self.tx_buffer).encode('hex'), self.socket.fileno(), self.socket.getsockname()), xbmc.LOGDEBUG)
		else:
			pass

	# this will be overridden in inherited class
	def handle_message(self, rx):
		pass

	# dummy function does nothing (if we're want to use native sockets we're using this function.
	def send_buffer(self):
		pass


# use native sockets instead
# TODO: not in use and fix this!
class TCPDaemonNative:

	# settings for TCP transport
	MAX_RECVBUFFER = 512

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

	def launch_tcp_daemon(self):

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
			self.rx_buffer = bytearray(self.socket.recv(self.MAX_RECVBUFFER))

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
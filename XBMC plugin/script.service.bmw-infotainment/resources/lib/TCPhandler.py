import asyncore
import threading
import socket
import time
import logging

# Python dev docs: http://mirrors.kodi.tv/docs/python-docs/13.0-gotham/
import xbmc, xbmcplugin, xbmcgui, xbmcaddon

__addon__		= xbmcaddon.Addon()
__addonname__	= __addon__.getAddonInfo('name')

MAX_RECVBUFFER = 512
PING_TIME = 3

PING = bytearray([0xAA, 0xAA, 0, 0, 0, 0, 0, 0])
INIT = bytearray(['h', 'i', 0, 0, 0, 0, 0, 0])
DISCONNECT = bytearray([0, 0, 0, 0, 0, 0, 0, 0])
REROUTE = 'ct'

# Base class			
class TCPClient(asyncore.dispatcher):

	def __init__(self):

		# init variables
		self.buffer = None
		self.connected = False

		# init dispatcher class
		asyncore.dispatcher.__init__(self)

		# DEBUG
		xbmc.log("BMW: init TCP class")

	def _reroute_connection(self, host, port):
		self.create_socket(socket.AF_INET, socket.SOCK_STREAM)
		self.connect( (host, port) )
		self.connected = True

		# update status in "settings"
		__addon__.setSetting("gateway.status", "Connected")
		
	#def handle_connect_event(self):
	#	self.connected = True

	#just when acting as server??
	def handle_connect(self):
		xbmc.log("BMW: Socket opened...")

	def handle_close(self):
		xbmc.log("BMW: Socket closed...")

		# update status in "settings"
		__addon__.setSetting("gateway.status", "Disconnected")

		self.connected = False
		self.close()

	def handle_read(self):
		rx_buf = self.recv(MAX_RECVBUFFER)
		self.handle_message(rx_buf)
		
	def writable(self):
		return True
		#return (len(self.buffer) > 0)

	def handle_write(self):
		if (self.buffer):
			sent = self.send(self.buffer)
			self.buffer = self.buffer[sent:]
			xbmc.log("BMW: writing to socket...")
		else:
			pass

	# this will be overridden in inherited class
	def handle_message(self, rx):
		pass

		
# ------------------------------------	
# alive signal
# ------------------------------------	

# daemon thread class for sending ping.
class AliveSignal(threading.Thread):

	def __init__(self):
		xbmc.log("BMW: INIT thread class for ping thread")
		self.thread = threading.Thread(name='PingThread', target=self._handler)
		self.thread.daemon = True
		self.connected = False

	#TODO: nothing will set 'self.connected' to False at the moment
	def _handler(self):
		while (self.connected):
			self.transmit_ping()
			time.sleep(PING_TIME)
		
	# this will be overridden in class inheritance
	def transmit_ping(self):
		pass


# extend 'TCPClient' and 'AliveSignal' base-classes with some functions
class MsgHandler(TCPClient, AliveSignal):

	def __init__(self):
		#TODO: is this right way to init class inheritance?
		self.n_pings = 0

		self.attempts = 0
		self.connected = False
		self.host = None
		self.port = None

		AliveSignal.__init__(self)
		super(MsgHandler, self).__init__()

	def start(self):

		# read new settings (if settings has changed)
		addon = xbmcaddon.Addon()

		# host and port from "settings.xml"
		self.host = addon.getSetting("gateway.ip-address")
		self.port = int( addon.getSetting("gateway.port") )

		# reset ping counter (if a restart occured)
		self.n_pings = 0

		# Connect
		self._reroute_connection(self.host, self.port)
		self.buffer = INIT
		xbmc.log("BMW: starting connection")

	def stop(self):

		# close connection gracefully by broadcast "close connection" to server!
		self.buffer = DISCONNECT

		# TODO: how to handle termination of "asynchore.loop" ?
		#self.close()


	def handle_message(self, rx):
		xbmc.log("BMW: received bytes on socket: %s" % rx.encode('hex') )
		#print "Thread: %s" %(self.get_ident())
		# connection closed will emit an empty message
		# special message (length 0) and reroute connection received!
		if len(rx):
			if (REROUTE in str( rx[0] + rx[1] )):
				self.close()
				route_port = int( str( rx[5] + rx[4] ).encode('hex'), 16 )

				self._reroute_connection(self.host, route_port)
				xbmc.log("BMW: rerouting to port %s ... (start ping thread)" % route_port)

				# TODO: throws an error when thread already has been started before.
				self.thread.start()


			elif (str( rx[0] + rx[1] ) in PING):
				self.recv_ping()
		else:
			xbmc.log("BMW: no length on message (disconnect message?)")

	#def handle_close_connection(self):
	#	print "sending close connection to server!"


	def recv_ping(self):
		xbmc.log("BMW: received Ping")
		self.last_ping = time.time()

	def transmit_ping(self):
		# send ping message
		self.buffer = PING

		#test disconnection
		self.n_pings += 1

		xbmc.log("BMW: Broadcasting ping (number %s)" % (self.n_pings))

		if (self.n_pings > 10):
			xbmc.log("BMW: 10 pings. disconnecting.")
			self.buffer = DISCONNECT
			#self._close_connection()

import asyncore
import threading
import socket
import time
import logging

# Python dev docs: http://mirrors.kodi.tv/docs/python-docs/13.0-gotham/
import xbmc, xbmcplugin, xbmcgui

# set up logger, no using XBMC instead.
#log = logging.getLogger("KODI-client.TCPClientHandler")
#print "this module's  name is: %s" %( __name__)

# usage:
# log.debug("DEBUG: Socket connected!")

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
		
	#def handle_connect_event(self):
	#	self.connected = True
	
	def handle_connect(self):
		xbmc.log("BMW: Socket connected!")

	def handle_close(self):
		xbmc.log("BMW: Socket closed...")
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
	
class AliveSignal(threading.Thread):

	def __init__(self):
		xbmc.log("BMW: INIT thread class")
		self.thread = threading.Thread(name='AliveSignalTransmitter', target=self._handler)
		self.thread.daemon = True
		self.connected = False

	#TODO: nothin will set 'self.connected' to False at the moment
	def _handler(self):
		while (self.connected):
			self.transmit_ping()
			time.sleep(PING_TIME)
		
	# this will be overridden in class inheritance
	def transmit_ping(self):
		pass


# extend 'TCPClient' and 'AliveSignal' base-classes with some functions
class MsgHandler(TCPClient, AliveSignal):

	def __init__(self, host, port):
		#TODO: is this right way to init class inheritance?
		self.n_pings = 0

		self.attempts = 0
		self.connected = False
		self.host = host
		self.port = port

		AliveSignal.__init__(self)
		super(MsgHandler, self).__init__()

	def start(self):
		self._reroute_connection(self.host, self.port)
		self.buffer = INIT
		xbmc.log("BMW: are we connected? %s", self.connected)

	def handle_message(self, rx):
		xbmc.log("BMW: received bytes on socket: %s", rx.encode('hex' ))
		#print "Thread: %s" %(self.get_ident())
		# connection closed will emit an empty message
		# special message (length 0) and reroute connection received!
		if len(rx):
			if (REROUTE in str( rx[0] + rx[1] )):
				self.close()
				route_port = int( str( rx[5] + rx[4] ).encode('hex'), 16 )

				self._reroute_connection(self.host, self.port)
				xbmc.log("BMW: rerouting to port %s ... (start ping thread)", route_port)
				#self.thread.start()
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
		self.buffer = PING

		#test disconnection
		self.n_pings = self.n_pings + 1

		if (self.n_pings > 3):
			xbmc.log("BMW: 5 pings. disconnecting.")
			self.buffer = DISCONNECT
			#self._close_connection()

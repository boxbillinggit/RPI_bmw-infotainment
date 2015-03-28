import asyncore
import threading
import socket
import time

MAX_RECVBUFFER = 512
PING_TIME = 3


# Base class			
class TCPClient(asyncore.dispatcher):

	def __init__(self):
		self.buffer = None
		self.connected = False
		asyncore.dispatcher.__init__(self)
		print "init TCP class"

	def _reroute_connection(self, host, port):
		self.create_socket(socket.AF_INET, socket.SOCK_STREAM)
		self.connect( (host, port) )
		self.connected = True
		
	#def handle_connect_event(self):
	#	self.connected = True
	
	def handle_connect(self):
		print "Socket connected!"

	def handle_close(self):
		print "Socket closed..."
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
			print "writing to socket..."
		else:
			pass

	#this will be overridden in inherited class
	def handle_message(self, rx):
		pass

		
# ------------------------------------	
# alive signal
# ------------------------------------	
	
class AliveSignal(threading.Thread):

	def __init__(self):
		print "INIT thread class"	
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

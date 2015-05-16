import socket
import errno
import threading
import time

MAX_RECVBUFFER = 512
PING_TIME = 3

class TCPClient:

	def __init__(self):
		self.connected = False

	def _reroute_connection(self, remote_host, remote_port):

		# TODO: put in a list? (if more sockets exists?)
		self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		
		try:
			self.socket.connect((remote_host, remote_port))
			
		except socket.error as err:
			if err.errno == errno.ECONNREFUSED:
				#print "hejkon pejkon.. : %s" %(e)
				print "Connection refused (no port available on host)"
			else:
				print "some other error: %s" %(err.strerror)
				
			return False
			
		self.connected = True
		self.listener = threading.Thread(name='TCP-Listener', target=self._listen)
		#self.listener.daemon = True		
		self.listener.start()
		
		# succeeded to connect?
		return True
			
	def _listen(self):
		while self.connected:
			rx = self.socket.recv(MAX_RECVBUFFER)
			
			# handle closed connections here?
			if rx:
				self.handle_message(rx)
			else:

				self._close_connection()
				
		# ended while loop.stop thread		
		#self.listener.stop()
		
	def _close_connection(self):
		#self.handle_close_connection()
		self.connected = False
		self.socket.close()

		
	# will be overridden in class inheritance
	def handle_message(self, rx):
		print "Received bytes: %s" %(rx)
		
	# will be overridden in class inheritance
	def handle_close_connection(self):
		print "connection closed!"	



# ------------------------------------	
# alive signal
# ------------------------------------	
	
class AliveSignal(threading.Thread):

	def __init__(self):
		print "INIT thread class"	
		self.thread = threading.Thread(name='AliveSignalTransmitter', target=self._handler)
		self.thread.daemon = True
		self.connected = False

	def _handler(self):
		while (self.connected):
			self.transmit_ping()
			time.sleep(PING_TIME)
	
	# this will be overridden in class inheritance
	def transmit_ping(self):
		pass

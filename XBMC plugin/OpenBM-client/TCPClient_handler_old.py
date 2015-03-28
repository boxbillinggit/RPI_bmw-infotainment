import socket
import threading
import SocketServer

import time

HOST = '192.168.1.68'
PORT = 4287


ACK_CONNECTED = 'ct'
PING_TIME = 3
ALIVE_TIMEOUT = 10

INIT = bytearray(['h', 'i', 0, 0, 0, 0, 0, 0])
PING = bytearray([0xAA, 0xAA, 0, 0, 0, 0, 0, 0])
DISCONNECT = bytearray([0, 0, 0, 0, 0, 0, 0, 0])

class TCPClient:

	def __init__(self):
		self.connected = False
		self.last_ping = 0
		self.n_reconnections = 0
		
	def _start_ping(self):
		threading.Timer(PING_TIME, self.ping).start()

	# TODO: make one single thread!
	# TODO: implement alive timeout check.
	def ping(self):
		
		# session is still alive
		if ( (time.time() - self.last_ping) < ALIVE_TIMEOUT) and self.connected:

			#while (self.connected):
			print "sending ping..."
			self.socket.send(PING)
			
			# ack
			buf = self.socket.recv(256)
			print(str(buf[0] + buf[1]).encode('hex'))
			self._recv_ping()
			self._start_ping()
		else:
			print "no ping received (or already disconnected).. Disconnecting! try re-connect?"
			print "last ping received: %s" %((time.time() - self.last_ping))
			self._reconnect()
			
			if (self.connected):
				self._disconnect()
		
	def _connect(self, remote_host, remote_port):
		self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		
		try:
			self.socket.connect((remote_host, remote_port))
		except socket.error, e:
			print "hejkon pejkon.. try again? : %s" %(e)
	
	def _reconnect(self):
		print "restart in a proper way (an un-intended disconnection was made)"
	
	def init_connect(self):
		self._connect(HOST, PORT)
		self.socket.send(INIT)
		
		#TODO: make a thread for this
		# wait for port to receive		
		buf = self.socket.recv(256)
		
		if ( ACK_CONNECTED in str( buf[0] + buf[1] ) ):
			port = int( str( buf[5] + buf[4] ).encode('hex'), 16 )
			self._redirect_connection(port)
		else:
			print "error. not port received"
			
	def _recv_ping(self):
		self.last_ping = time.time()
			
	def _redirect_connection(self, port):
		print "PORT received. (redirected to port '%s')" %(port)
		self._disconnect()
		self._connect(HOST, port)
		self.connected = True
		self.last_ping = time.time()
		self._start_ping()

	def _disconnect(self):
		self.socket.send(DISCONNECT)	
		self.connected = False		
		self.socket.close()

import asyncore
import socket
import threading
import time

# import client lib
from lib.TCPClientHandlerAsyncore import *


HOST = '192.168.1.68'
PORT = 4287

PING = bytearray([0xAA, 0xAA, 0, 0, 0, 0, 0, 0])
INIT = bytearray(['h', 'i', 0, 0, 0, 0, 0, 0])
DISCONNECT = bytearray([0, 0, 0, 0, 0, 0, 0, 0])
REROUTE = 'ct'

RECONNECT = 1


# extend 'TCPClient' and 'AliveSignal' base-classes with some functions
class MsgHandler(TCPClient, AliveSignal):

	def __init__(self):
		#TODO: is this right way to init class inheritance?
		self.n_pings = 0
		
		self.reconnections = 0
		self.connected = False
		AliveSignal.__init__(self)
		super(MsgHandler, self).__init__()
		
	def init_connect(self, host, port):
		self._reroute_connection(host, port)
		self.buffer = INIT
		print "are we connected? %s" %(self.connected)
		
	def handle_message(self, rx):
		print "received bytes on socket: %s" %(rx.encode('hex'))
		#print "Thread: %s" %(self.get_ident())
		# connection closed will emit an empty message
		# special message (length 0) and reroute connection received!
		if len(rx):
			if (REROUTE in str( rx[0] + rx[1] )):
				self.close()
				port = int( str( rx[5] + rx[4] ).encode('hex'), 16 )
				self._reroute_connection(HOST, port)
				print "rerouting to port %s ... (start ping thread)" %(port)
				#self.thread.start()
				self.thread.start()

				
			elif (str( rx[0] + rx[1] ) in PING):
				self.recv_ping()
		else:
			print "no length on message"
			
	#def handle_close_connection(self):
	#	print "sending close connection to server!"
		
	
	def recv_ping(self):
		print "received Ping"
		self.last_ping = time.time()

	def transmit_ping(self):
		self.buffer = PING
		
		#test disconnection		
		self.n_pings = self.n_pings + 1
		
		if (self.n_pings > 3):
			print "5 pings. disconnecting:"
			self.buffer = DISCONNECT
			#self._close_connection()
			
				
client = MsgHandler()

def TCPClientThread():
	while (client.reconnections < RECONNECT):
		client.reconnections = client.reconnections + 1
		client.init_connect(HOST, PORT)	
		asyncore.loop()
		print "END: connection lost. try reconnecting (attempt %s).." %(client.reconnections)

if __name__ == "__main__":
	
	# start the server thread
	threading.Thread(name='TCPServerThread', target=TCPClientThread).start()

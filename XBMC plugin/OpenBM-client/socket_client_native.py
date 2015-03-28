import asyncore
import socket
import threading
import time

# import client lib
from lib import *


HOST = '192.168.1.68'
PORT = 4287

PING = bytearray([0xAA, 0xAA, 0, 0, 0, 0, 0, 0])
INIT = bytearray(['h', 'i', 0, 0, 0, 0, 0, 0])
DISCONNECT = bytearray([0, 0, 0, 0, 0, 0, 0, 0])

REROUTE = 'ct'



# extend 'TCPClient' and 'AliveSignal' base-classes with some functions
class MsgHandler(TCPClient, AliveSignal):

	def __init__(self):
		#TODO: is this right way to class inheritance?
		self.n_pings = 0
		AliveSignal.__init__(self)
		super(MsgHandler, self).__init__()
				
	def init_connect(self, host, port):
		if ( self._reroute_connection(host, port) ):
			self.socket.send(INIT)
			
	def handle_message(self, rx):
		print "received bytes on socket:"
		#print "Thread: %s" %(self.get_ident())
		# connection closed will emit an empty message
		# special message (length 0) and reroute connection received!
		if len(rx):
			if (REROUTE in str( rx[0] + rx[1] )):
			
				#self.close()
				self.socket.close()
				port = int( str( rx[5] + rx[4] ).encode('hex'), 16 )
				if ( self._reroute_connection(HOST, port) ):
					
					print "start PING routine!"
					self.thread.start()
					
					#test
					self.transmit_ping()
				
			elif (str( rx[0] + rx[1] ) in PING):
				self.recv_ping()
				
	#def handle_close_connection(self):
	#	print "sending close connection to server!"
		
	
	def recv_ping(self):
		print "received Ping"
		self.last_ping = time.time()

	def transmit_ping(self):
		self.socket.send(PING)
		self.n_pings = self.n_pings + 1
		
		#test disconnection
		if (self.n_pings > 5):
			print "5 pings. disconnecting:"
			self.socket.send(DISCONNECT)
			self._close_connection()
			
				
client = MsgHandler()

# tvo saker:
# 1. threading (main thread and child threads?
# 2. sending message immediately

if __name__ == "__main__":

	##TODO: make a separate thread from this
	client.init_connect(HOST, PORT)
	
	# for async
	#asyncore.loop(0.01)
	#print "connection lost"
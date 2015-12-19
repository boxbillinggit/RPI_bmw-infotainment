
"""
Ref: https://docs.python.org/2/library/socketserver.html

"""
__author__ = 'lars'

import sys, os
import socket
import threading
import SocketServer


# TCP/IP protocol settings
HEADER_LENGTH = 8

TERMINAL_END = "\r\n"


# print a well formed HEX-string from type "bytearray"
def to_hexstr(data):

	return " ".join(map(lambda byte: "%X" % byte, data)) if data else ""


# adjust header to correct length (8byte)
def resize_header(data):

	if len(data) <= 8:
		return data + ([0] * (HEADER_LENGTH - len(data)))
		#return data + (chr(0) * (HEADER_LENGTH - len(data)))


# TCP protocol headers. (also resize header to 8byte)
#PING 		= resize_header([0xAA, 0xAA])
CONNECT 	= resize_header([0x68, 0x69])	# ASCII: 'hi'
#CONNECT 	= resize_header("hi")	# ASCII: 'hi'
#DISCONNECT 	= resize_header([])
#REROUTE 	= [0x63, 0x74, 0x00, 0x00, 0xC0, 0x10]		# ASCII: 'ct' + [port]
REROUTE = [0x63, 0x74]

HOST, PORT = "0.0.0.0", 4287
ALIVE_TIMEOUT = 10
MAX_RECV = 1024

# Debug flags
ALLOW_REROUTE = True


messages = {
	"hi": bytearray(REROUTE),
}

# https://docs.python.org/2/library/socketserver.html

# <port>:<socket>
clients = {}


def create_server(port):

	try:
		server = GatewayClientServer((HOST, port), GatewayClientHandler)
	except socket.error as err:
		print "FAIL - Could not start server on port %d: %s" % (port, err.strerror)
		return None

	clients.update([(port, server)])

	# Start a thread with the server -- that thread will then start one
	# more thread for each request
	server_thread = threading.Thread(target=server.handle_request)

	# Exit the server thread when the main thread terminates
	server_thread.daemon = True
	server_thread.start()

	print "New server running in thread:", server_thread.name

	return server


def reroute_to_port(port):

	data = resize_header(REROUTE)

	# insert port
	data[4] = port & 0xFF
	data[5] = port >> 8 & 0xFF

	print "DEBUG - sending reroute request to port %s..." % port

	return bytearray(data)


class GatewayMainHandler(SocketServer.BaseRequestHandler):

	def handle(self):

		self.request.settimeout(ALIVE_TIMEOUT)

		try:
			data = self.request.recv(MAX_RECV)
		except socket.timeout:
			return

		if bytearray(data) == bytearray(CONNECT) or "hi"+TERMINAL_END in data:

			# start new server on highest port number +1
			port = (max(clients.keys() + [PORT]) + 1)

			# send reroute request - if succeeded to create a server
			if create_server(port):
				self.request.sendall(reroute_to_port(port))


class GatewayClientHandler(SocketServer.BaseRequestHandler):

	def handle(self):

		self.request.settimeout(ALIVE_TIMEOUT)
		cur_thread = threading.current_thread()

		while True:

			try:
				data = self.request.recv(MAX_RECV)
			except socket.timeout:
				break

			if not data or data == TERMINAL_END:
				break

			print "DEBUG - {} received: {}".format(cur_thread.name, to_hexstr(bytearray(data)))
			self.request.sendall("echo\n")

	def finish(self):

		# timed-out - client has not transmitted any data, remove server.
		# TODO: closes server connection - but does not free port! (after a while port is free)
		self.server.server_close()



class GatewayClientServer(SocketServer.ThreadingMixIn, SocketServer.TCPServer):

	"""
	This class handles all clients connecting to routed port.
	Methods specific to servers started with 'handle_request()'
	"""

	timeout = ALIVE_TIMEOUT

	def __init__(self, server_address, RequestHandlerClass):

		# self.shutdown_requested = False
		SocketServer.TCPServer.__init__(self, server_address, RequestHandlerClass)

	# if we don't receive any connections within a period of time - remove server and close connection
	def handle_timeout(self):

		self.server_close()

	def server_close(self):

		# remove servers from reference list
		ip, port = self.server_address

		print "DEBUG - removing server port %d" % port

		try:
			clients.pop(port)
		except KeyError:
			print "ERROR - could not find server instance i list"

		try:
			self.socket.shutdown(socket.SHUT_RDWR)
			self.socket.close()
		except socket.error as err:
			print "ERROR - could not shutdown socket - %s" % err.strerror





class GatewayMainServer(SocketServer.ThreadingMixIn, SocketServer.TCPServer):

	"""
	This class is dedicated to servers started with 'server_forever()'
	"""

	def __init__(self, server_address, RequestHandlerClass):

		SocketServer.TCPServer.__init__(self, server_address, RequestHandlerClass)

	def server_close(self):

		# shutdown child servers
		for port in clients:

			try:
				#clients.get(port).server_close()
				clients.get(port).socket.shutdown(socket.SHUT_RDWR)
				clients.get(port).socket.close()
			except KeyError:
				print "DEBUG - could not remove server on port %d, already removed?" % port

		# clear clients reference list
		clients.clear()

		# shutdown main server.
		# TODO does not shutdown active connections! (only disable accepts)
		self.socket.shutdown(socket.SHUT_RDWR)
		self.socket.close()


class Gateway(object):

	"""
	Main class starting the main server available in 'PORT' when created.
	"""

	def __init__(self):

		try:
			server = GatewayMainServer((HOST, PORT), GatewayMainHandler)
		except socket.error as err:
			print "ERROR - Could not start main server (on port %d): %s" % (PORT, err.strerror)
			return

		# Start a thread with the server -- that thread will then start one
		# more thread for each request
		server_thread = threading.Thread(target=server.serve_forever)

		# Exit the server thread when the main thread terminates
		server_thread.daemon = False
		server_thread.start()

		print "Main server running in thread:", server_thread.name

		self.server = server

	def __del__(self):

		try:
			self.server.shutdown()
			self.server.server_close()
		except AttributeError:
			print "no server to remove"

	def send(self):
		# TODO: send to all clients connected
		pass


if __name__ == "__main__":

	gateway = Gateway()

	print ("Bye!")

# use select along with non-blocking sockets? instead:
# https://docs.python.org/3/library/select.html?highlight=select.select#select.select
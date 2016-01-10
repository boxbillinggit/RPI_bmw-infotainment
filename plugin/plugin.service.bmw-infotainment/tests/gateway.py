"""
Ref:
https://docs.python.org/2/library/socketserver.html
"""

import socket
import threading
import SocketServer
import time

__author__ = 'lars'

# TCP/IP protocol settings
HOST			= "0.0.0.0"
PORT			= 4287
HEADER_LENGTH 	= 8
MAX_RECV 		= 1024
ALIVE_TIMEOUT 	= 10
PORT_RANGE 		= 8

TERMINAL_END = "\r\n"

# <port>:<server-instance>
client_servers = {}
client_socks = []

# echo the sent signals back to client...
ECHO = True
FAIL_TO_REROUTE = False


def resize_header(data):
	"""
	Adjust header to correct length (8byte)
	"""
	if len(data) <= 8:
		return data + ([0] * (HEADER_LENGTH - len(data)))

# TCP protocol headers. TODO: get definitions from TCPIP_handler-class instead.
PING 		= resize_header([0xAA, 0xAA])
CONNECT 	= resize_header(list("hi"))
DISCONNECT 	= resize_header([])
REROUTE 	= list("ct")


def current_thread():
	return threading.current_thread().name


def hexstring(data):
	"""
	Print a well formed HEX-string from type "bytearray"
	"""
	return " ".join(map(lambda byte: "%X" % byte, data)) if data else ""


def create_server(port):

	"""
	Start a thread with the server -- that thread will then start one
	more thread for each request. Exit the server when the main-
	thread terminates since this thread is daemonic.
	"""

	if FAIL_TO_REROUTE:
		return True

	try:
		server = GatewayClientServer((HOST, port), GatewayClientHandler)
	except socket.error as err:
		print "ERROR - {} - could not start server on port {}: {}".format(current_thread(), port, err.strerror)
		return None

	client_servers.update([(port, server)])

	server_thread = threading.Thread(target=server.handle_request)
	server_thread.daemon = True
	server_thread.start()

	return True


def reroute_to_port(port):

	"""
	Create header for a reroute-request.
	"""

	data = resize_header(REROUTE)

	# insert port
	data[4] = port & 0xFF
	data[5] = port >> 8 & 0xFF

	return bytearray(data)


def create_frame(msg):

	"""
	Create TCP/IP-frame from 3-tuple: ([src], [dst], [data])
	"""

	src, dst, data = msg

	# create header and insert length
	header = resize_header(src+dst)
	header[2] = len(data)

	return bytearray(header+data)


class GatewayMainHandler(SocketServer.BaseRequestHandler):

	"""
	Main handler for receiving data on socket -and reroute client to
	another port.
	"""

	def handle(self):

		self.request.settimeout(ALIVE_TIMEOUT)

		try:
			data = self.request.recv(MAX_RECV)
		except socket.timeout:
			return

		if bytearray(data) == bytearray(CONNECT) or "hi"+TERMINAL_END in data:

			# start new server on highest port number +1
			port = (max(client_servers.keys() + [PORT+1]))

			# increase port number if port is busy (failed to create server)
			while not create_server(port) and port in range(PORT, (PORT+PORT_RANGE)):
				port += 1

			self.request.sendall(reroute_to_port(port))


class GatewayClientHandler(SocketServer.BaseRequestHandler):

	"""
	Main handler for handling messages from one client.

	Receive data until "shutdown_requested". recv() has a timeout and will poll
	periodic. Hence if "shutdown_requested" is set, we make a graceful shutdown
	when next data receives, or when the timeout occurs.
	"""

	def handle(self):

		self.request.settimeout(ALIVE_TIMEOUT)

		while not self.server.shutdown_requested:

			try:
				data = self.request.recv(MAX_RECV)
			except socket.timeout:
				break

			if not data or data == TERMINAL_END or bytearray(data) == bytearray(DISCONNECT):
				break

			print "DEBUG - {} - received: {}".format(current_thread(), hexstring(bytearray(data)))

			if ECHO:
				self.request.sendall(data)

	def finish(self):
		"""
		timed-out - client has not transmitted any data in a period of time, remove server.
		"""
		self.server.server_close()


class GatewayClientServer(SocketServer.ThreadingMixIn, SocketServer.TCPServer):

	"""
	This class contain methods specific to servers started with "handle_request()"
	"""

	def __init__(self, server_address, RequestHandlerClass):

		SocketServer.TCPServer.__init__(self, server_address, RequestHandlerClass)
		self.shutdown_requested = False
		self.timeout = ALIVE_TIMEOUT

	def handle_timeout(self):

		"""
		If we don't receive any connections from the client within a period of
		time - remove server and close connection.
		"""

		self.server_close()

	def get_request(self):

		"""
		Get the request and client address from the socket.
		"""

		sockfd, client_address = self.socket.accept()
		client_socks.append(sockfd)

		return sockfd, client_address

	def close_request(self, sockfd):

		"""
		Called to clean up an individual request. remove socket fom clients list
		"""

		client_socks.remove(sockfd)
		sockfd.close()

	def server_activate(self):
		"""
		Called by constructor to activate the server.
		"""
		print "INFO - {} - new client server running on port: {}".format(current_thread(), self.server_address[Gateway.PORT])
		self.socket.listen(self.request_queue_size)

	def server_close(self):

		"""
		Close server and remove servers from the list
		"""

		ip, port = self.server_address

		print "DEBUG - {} - removing server port: {}".format(current_thread(), port)

		try:
			client_servers.pop(port)
		except KeyError:
			print "ERROR - {} - could not find server instance i list".format(current_thread())

		try:
			self.socket.shutdown(socket.SHUT_RDWR)
			self.socket.close()
		except socket.error as err:
			print "ERROR - {} - could not shutdown socket: {}" .format(current_thread(), err.strerror)


class GatewayMainServer(SocketServer.ThreadingMixIn, SocketServer.TCPServer):

	"""
	This class is dedicated to servers started with 'server_forever()'
	"""

	def __init__(self, server_address, RequestHandlerClass):

		SocketServer.TCPServer.__init__(self, server_address, RequestHandlerClass)

	def server_activate(self):
		"""
		Called by constructor to activate the server.
		"""
		print "INFO - {} - Gateway running on port: {}".format(current_thread(), self.server_address[Gateway.PORT])
		self.socket.listen(self.request_queue_size)

	def server_close(self):

		self.socket.shutdown(socket.SHUT_RDWR)
		self.socket.close()


class Gateway(object):

	"""
	Main class starting the main server available in 'PORT' when created.
	"""

	IP, PORT = range(2)

	def __init__(self):
		self.server = None

	def start(self):

		"""
		Start the gateway service.
		"""

		try:
			server = GatewayMainServer((HOST, PORT), GatewayMainHandler)
			self.server = server
		except socket.error as err:
			print "ERROR - {} - could not start Gateway on port {}: {}".format(current_thread(), PORT, err.strerror)
			return

		server_thread = threading.Thread(target=server.serve_forever)
		server_thread.daemon = False
		server_thread.start()

	def stop(self):

		"""
		Shutdown Gateway service gracefully - also disconnects client child-servers
		"""

		try:
			self.server.shutdown()
			self.server.server_close()
		except AttributeError:
			print "ERROR - {} - No server to remove".format(current_thread())

		disconnect()


def broadcast(messages, wait=0.5):

	"""
	Broadcast a message to all clients connected.

	"msg" is list of 3-tuple: [([src], [dst], [data]), ...]
	"""

	for sockfd in client_socks:

		for msg in messages:
			data = create_frame(msg)
			sockfd.send(data)

			print "DEBUG - {} - sending: {}".format(threading.currentThread().name, hexstring(data))

			if wait:
				time.sleep(wait)


def broadcast_raw(msg):

	"""
	broadcast a raw bytearray
	"""

	for sockfd in client_socks:
		sockfd.send(msg)


def disconnect():

	"""
	Gracefully disconnect all clients-servers - but keep main gateway-server running.
	"""

	for port in client_servers:
		client_servers.get(port).shutdown_requested = True

__author__ = 'Lars'

import time
from threading import Thread
from TCPdaemon import TCPDaemonAsyncore

# Python dev docs: http://mirrors.kodi.tv/docs/python-docs/14.x-helix/
import xbmc, xbmcplugin, xbmcgui, xbmcaddon

__addon__		= xbmcaddon.Addon()
__addonname__	= __addon__.getAddonInfo('name')

# initiate a monitor
monitor = xbmc.Monitor()

# TODO: special log wrapper (if we're want to use class -and log outside XBMC/KODI)
class XBMCHandler:
	def __init__(self):
		pass

	def log(arg, level):
		xbmc.log(arg, level)

# handler for the TCP protocol.
class TCPHandler(TCPDaemonAsyncore):

	# TCP protocol settings
	HEADER_LENGTH = 8
	PING_TIME_INTERVAL = 3

	# TCP protocol headers (TODO: must refactor length before use)
	PING = [0xAA, 0xAA]
	#REROUTE = [0x63, 0x74]	# ASCII: 'ct'
	REROUTE = 'ct'
	CONNECT = [0x68, 0x69]	# ASCII: 'hi'
	DISCONNECT = []

	# init the class
	def __init__(self):

		# inherited from class 'TCPDaemon' (placeholder)
		self.tx_buffer = None

		# counter for ping thread.
		self.pings_rx = 0
		self.pings_tx = 0
		self.ping_rx_timestamp = 0

		# connection specefic data
		self.attempts = 0
		self.host = None
		self.port = None

		# data for handling the TCP frame
		self.awaiting_data_packet = False
		self.dst = None
		self.src = None
		self.len_data = None

		# TODO: is this right way to init class inheritance? (difference between superclass and old-style class??)
		TCPDaemonAsyncore.__init__(self)

	# adjust header to right length (looks more proper than writing a lot of zeroes in message definition above)
	def reform_header(self, msg):
		return msg + ([0] * (self.HEADER_LENGTH - len(msg)))

	# start connection
	def start(self):

		self.attempts += 1

		# TODO: put XBMC/KODI specific things in a separate class?
		# read new ip settings (if settings has changed)
		addon = xbmcaddon.Addon()

		# host and port from "settings.xml"
		self.host = addon.getSetting("gateway.ip-address")
		self.port = int(addon.getSetting("gateway.port"))

		# Connect. (function inherited from class 'TCPDaemon')
		self.reroute_connection(self.host, self.port)

		# adjust size of header to 'HEADER_LENGTH' (fill with zeroes until length is correct)
		self.tx_buffer = self.reform_header(self.CONNECT)
		self.send_buffer()

		# log.
		xbmc.log("BMW: starting connection", xbmc.LOGINFO)

		# inherited from 'TCPDaemon' class (blocking function)
		self.launch_tcp_daemon()

	# Terminate socket
	def stop(self):

		# close connection gracefully by broadcast "close connection" to server!
		if self.is_connected():

			# log.
			xbmc.log("BMW: Request to disconnect. Sending disconnect to server (server will close socket for us)..", xbmc.LOGDEBUG)

			# adjust size of header to 'HEADER_LENGTH' (fill with zeroes until length is correct)
			self.tx_buffer = self.reform_header(self.DISCONNECT)
			self.send_buffer()

		# not connected, just terminate socket.
		else:
			xbmc.log("BMW: Request to disconnect. we are not connected so we closing socket. ", xbmc.LOGDEBUG)

			# close socket
			self.close()

	# handles the received TCP frames.
	# this is called from 'TCPDaemon' class
	def handle_message(self, rx):
		xbmc.log("BMW: received bytes on socket: %s" % str(rx).encode('hex'), xbmc.LOGDEBUG)

		# we have 3 possibilities:
		#
		# * header has no length: disconnect message from OpenBM-daemon.
		# * header only (data length is zero): special TCP message.
		# * data length is not zero: we have a IBUS message to parse.

		def no_length():
			xbmc.log("BMW: no length on TCP frame", xbmc.LOGDEBUG)

		# TODO: rewrite this (how -and where to convert between array <---> bytearray??
		def header_only():
			xbmc.log("BMW: received header only.", xbmc.LOGDEBUG)

			if self.REROUTE in rx:

				# reform to base-16 (not very easy though)
				_rx = map(chr, self.rx_buffer)
				self.port = int((_rx[5]+_rx[4]).encode('hex'), 16)

				# TODO: should be in 'TCPDaemon' class instead?
				self.close()

				# function inherited from class 'TCPDaemon'
				self.reroute_connection(self.host, self.port)

				# start a ping thread.
				self.launch_ping_daemon()


			elif rx == bytearray(self.reform_header(self.PING)):
				self.rx_ping()

			else:
				content_err()

		def data_packet(src, dst, data):
			xbmc.log("BMW: TODO: parse IBUS message.", xbmc.LOGDEBUG)

		# error functions.
		def length_err():
			xbmc.log("ERROR: unexpected length.", xbmc.LOGERROR)

		def content_err():
			xbmc.log("ERROR: unexpected content.", xbmc.LOGERROR)

		# Parse TCP frame from protocol definition
		def parse_tcp_frame():

			# TCP frame length
			length = len(rx)

			# empty TCP frame received.
			if not length:
				no_length()

			# we have received some data...
			else:

				# this is type 'bytearray'
				len_data = rx[2]

				# header is already received, this TCP frame contains the data packet.
				if self.awaiting_data_packet:

					# Check if length is as expected
					if length == self.len_data:
						# use src and dst stored from previous received header.
						data_packet(self.src, self.dst, rx)

					else:
						length_err()


					# reset flag
					self.awaiting_data_packet = False

				# do we have header+data in this TCP frame?
				elif len_data and length == (self.HEADER_LENGTH + len_data):

					INDEX = (self.HEADER_LENGTH-1)

					# data is located after the header
					data = rx[INDEX:]
					self.src = rx[0]
					self.dst = rx[1]
					self.len_data = rx[2]

					data_packet(self.src, self.dst, data)

				# nope, data packet is sent separate in the next TCP frame.
				elif len_data and (length < (self.HEADER_LENGTH + len_data)):

					# save dst and src until data packet is received
					self.src = rx[0]
					self.dst = rx[1]
					self.len_data = rx[2]

					# set flag awaiting data
					self.awaiting_data_packet = True

				# TCP protocol message
				elif not len_data:
					header_only()

				# some error occured
				else:
					length_err()

					# clear flag (some error occured)
					self.awaiting_data_packet = False


		# Start parsing the frame
		parse_tcp_frame()


	# request to start the ping daemon
	def launch_ping_daemon(self):

		# reset ping counters (if a restart occured)
		self.pings_rx = 0
		self.pings_tx = 0

		# launch new thread
		thread = Thread(name='PingDaemon', target=self.ping_daemon)
		thread.daemon = True
		thread.start()

	# runs in a separate thread
	def ping_daemon(self):

		# log
		xbmc.log("BMW: starting ping daemon", xbmc.LOGDEBUG)

		# loop until abort is requested from XBMC
		# TODO: how about init of monitor? put all XBMC/KODI in a separate class?
		while not monitor.abortRequested():

			# terminate thread if we're not connected.
			if not self.is_connected():
				break

			self.tx_ping()
			time.sleep(self.PING_TIME_INTERVAL)

		# log
		xbmc.log("BMW: terminating ping thread (function returns)", xbmc.LOGDEBUG)


	# ping received
	def rx_ping(self):

		xbmc.log("BMW: receiving ping (number: %s, last received: %s [s] ago )" % (self.pings_rx, (time.time() - self.ping_rx_timestamp)), xbmc.LOGDEBUG)

		# increase counter, capture timestamp
		self.pings_rx += 1
		self.ping_rx_timestamp = time.time()

	# ping transmitted
	def tx_ping(self):

		xbmc.log("BMW: sending ping (number: %s)" % (self.pings_tx), xbmc.LOGDEBUG)

		# increase counter
		self.pings_tx += 1

		# send ping message (refactor length to exactly 8 bytes)
		self.tx_buffer = self.reform_header(self.PING)
		self.send_buffer()

		# DEBUG
		if (self.pings_tx > 20):
			xbmc.log("BMW: DEBUG - 20 pings transmitted, disconnecting.", xbmc.LOGDEBUG)
			self.stop()


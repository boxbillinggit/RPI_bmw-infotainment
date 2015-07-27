__author__ = 'Lars'
# this module handles the overlay TCP protocol and functions

# TODO: restructure module (names, classes, and more)
# TODO: look over all loglevels -and log messages (decrease amount?)
# TODO: implement tx of IBUS-messages

# about loglevels:
# http://kodi.wiki/view/Log_file/Advanced#advancedsettings.xml_for_normal_debugging

try:
	# Python dev docs: http://mirrors.kodi.tv/docs/python-docs/14.x-helix/
	import xbmc, xbmcplugin, xbmcgui, xbmcaddon

except ImportError as err:
	print "%s: %s - using 'XBMCdebug'-modules instead" % (__name__, err.message)
	import debug.XBMC as xbmc
	import debug.XBMCGUI as xbmcgui
	import debug.XBMCADDON as xbmcaddon

__monitor__ 	= xbmc.Monitor()
__addon__		= xbmcaddon.Addon()
__addonname__	= __addon__.getAddonInfo('name')
__addonid__		= __addon__.getAddonInfo('id')

# import built-in libraries
import time
from threading import Thread

# import the script's libraries
from TCPIPSocket import TCPIPSocketAsyncore, to_hexstr
from IBUSHandler import Filter
import settings


# TCP/IP protocol settings
HEADER_LENGTH = 8
PING_TIME_INTERVAL = 3		# seconds
NO_LENGTH=0

# adjust header to correct length (8byte)
def _resize_header(data):
	return data + ([0] * (HEADER_LENGTH - len(data)))

# TCP protocol headers. (also resize header to 8byte)
PING 		= _resize_header([0xAA, 0xAA])
CONNECT 	= _resize_header([0x68, 0x69])	# ASCII: 'hi'
DISCONNECT 	= _resize_header([])
REROUTE 	= [0x63, 0x74]					# ASCII: 'ct'

#
# static methods
#


def rx_no_frame_length():
	xbmc.log("%s: No length on TCP/IP-frame. (disconnect message from server)" % __addonid__, xbmc.LOGDEBUG)


def rx_err_length(rx_buf_len, data_len, rx_buf):
	xbmc.log("%s - Unexpected rx length. (current buffer length:%d, expected:%d, frame: [%s]" % (__addonid__, rx_buf_len, data_len, to_hexstr(rx_buf)), xbmc.LOGERROR)


def rx_err_header_content(rx_buf):
	xbmc.log('%s - Unexpected rx header content. [%s]' % (__addonid__, to_hexstr(rx_buf)), xbmc.LOGERROR)


# Base class handler for the TCP protocol. Main point for routing Rx -and Tx data.
class TCPIPHandler(object):

	# init the class
	def __init__(self):

		# data for handling the TCP/IP frame
		self.header_received = False
		self.dst = None
		self.src = None
		self.data = list()
		self.data_len = 0

		# init TCP/IP-socket
		self.tcp_ip_socket = TCPIPSocketAsyncore()
		self.tcp_ip_socket.handle_message = self.rx_tcp_ip_buf

		# init TCP/IP-daemon
		self.tcp_ip_daemon = TCPIPDaemon(self.tcp_ip_socket)
		self.start = self.tcp_ip_daemon.start
		self.stop = self.tcp_ip_daemon.stop

		# init ping transmitter
		self.ping_daemon = PingDaemon(self.tcp_ip_socket)

		# init IBUS handler
		self.ibus_handler = Filter()

		xbmc.log("%s: %s - init class." % (__addonid__, self.__class__.__name__), xbmc.LOGDEBUG)

	def debug_recv_rxbuf(self, strbuf):

		if not len(strbuf):
			return

		# split buffer to separate bytes
		buf = strbuf.split(" ")

		# convert string to bytes
		self.tcp_ip_socket.rx_buffer = map(lambda str: int(str, 16), buf)

		# execute
		self.rx_tcp_ip_buf()

	def rx_tcp_ip_buf(self):

		"""
		Main function for handling the received TCP/IP frames.

		We have 3 states for the TCP/IP-communication:

		 * header+data+header... Parse out header chunk -and loop over
		 * data+header.data... Parse out data chunk -and loop over
		 * error (unexpected length)
		"""

		rx_buf = self.tcp_ip_socket.rx_buffer

		# disconnect message
		if not len(rx_buf):
			rx_no_frame_length()

		# parse TCP/IP-frame:
		else:

			while len(rx_buf):

				rx_buf_len = len(rx_buf)

				# data+header+data...
				if self.header_received:

					bytes_handled = self.rx_data_chunk(rx_buf)

					# clear this for logging purpose.
					self.data_len = 0

				# header+data+header...
				elif rx_buf_len >= HEADER_LENGTH:

					# if length is zero we have an special overlay TCP/IP-protocol message. else its a part of a message
					if rx_buf[2]:
						self.rx_header_chunk(rx_buf)
					else:
						self.rx_special_header(rx_buf)

					bytes_handled = HEADER_LENGTH

				else:
					rx_err_length(rx_buf_len, (HEADER_LENGTH+self.data_len), rx_buf)

					# fault-handling: empty complete buffer?, clear flag
					bytes_handled = rx_buf_len
					self.header_received = False

				# empty buffer for bytes handled -and loop over.
				rx_buf = rx_buf[bytes_handled:]

	# Header only. Handle the special overlay TCP/IP-protocol message.
	def rx_special_header(self, rx_buf):

		if bytearray(REROUTE) in rx_buf:

			# encode to base-16, and in reverse order (DOOH! not so easy..)
			_rx = map(chr, rx_buf)
			_port = int((_rx[5]+_rx[4]).encode('hex'), 16)

			# close connection...
			self.tcp_ip_socket.close()

			# ...and reroute to new port!
			self.tcp_ip_socket.reroute_connection(self.tcp_ip_daemon.host, _port)

			# start a ping thread.
			self.ping_daemon.start()

		elif bytearray(PING) == rx_buf:
			self.ping_daemon.rx_ping()

		else:
			rx_err_header_content(rx_buf)

	def rx_header_chunk(self, rx_buf):
		xbmc.log("%s: %s - 'header' parsed." % (__addonid__, self.__class__.__name__), xbmc.LOGDEBUG)

		# save data from header -and wait for next TCP/IP-frame
		self.header_received = True

		self.src = rx_buf[0]
		self.dst = rx_buf[1]
		self.data_len = rx_buf[2]

	# header is already received, parse out the data frame.
	def rx_data_chunk(self, rx_buf):

		# DEBUG
		xbmc.log("%s: %s - 'data' parsed." % (__addonid__, self.__class__.__name__), xbmc.LOGDEBUG)

		# get data chunk length from previous received header
		data_chunk_len = self.data_len

		# TODO: if not complete frame is received, wait until next loop(=loop4ever)? -or abort?
		if len(rx_buf) < data_chunk_len:
			rx_err_length(len(rx_buf), data_chunk_len, rx_buf)
			self.header_received = False
			return len(rx_buf)

		# find event
		self.ibus_handler.find_event(self.src, self.dst, rx_buf[:data_chunk_len])

		# clear flag
		self.header_received = False

		# return bytes parsed
		return data_chunk_len

class TCPIPDaemon(object):

	def __init__(self, tcp_ip_socket):

		# socket instance
		self.tcp_ip_socket = tcp_ip_socket

		# connection specific data
		self.attempts = 0
		self.abort_requested = False
		self.host = None
		self.port = None

	# start TCP/IP daemon service thread
	def start(self):

		if self.tcp_ip_socket.is_connected():
			xbmc.log("%s: %s - Request to start service - we are already connected" % (__addonid__, self.__class__.__name__), xbmc.LOGDEBUG)

		else:
			# we're starting over again
			self.abort_requested = False

			# launch the service thread...
			t = Thread(name='BMW-Service', target=self._tcp_daemon)
			t.daemon = True
			t.start()

	# Terminate TCP/IP daemon service thread
	def stop(self):

		# reset connection attempts also.
		self.attempts = 0

		# we force the TCP daemon to stop
		self.abort_requested = True

		# close connection gracefully by broadcast "close connection" to server!
		if self.tcp_ip_socket.connected:

			# log.
			xbmc.log("%s: %s - Request to disconnect, sending disconnect to server." % (__addonid__, self.__class__.__name__), xbmc.LOGDEBUG)

			# send 'disconnect'
			self.tcp_ip_socket.send_buffer(DISCONNECT)

		# not connected, just terminate socket.
		else:
			xbmc.log("%s: %s - Request to disconnect, already disconnected " % (__addonid__, self.__class__.__name__), xbmc.LOGDEBUG)

			# close socket
			self.tcp_ip_socket.close()


	# TCP/IP service thread.
	def _tcp_daemon(self):

		# Consider if we're terminating, otherwise just loop over again (restart connection).
		while self.attempts < settings.MAX_RECONNECT and not (__monitor__.abortRequested() or self.abort_requested):

			dialog = xbmcgui.Dialog()

			# ask user to reconnect (if not the first initial connection attempt)
			if self.attempts and not dialog.yesno(__addonid__, "Connection lost... (attempt: %s)" % self.attempts, "Reconnect?" ):
				break

			self.attempts += 1

			# read new ip-settings (hence we cant use __addon__ if settings has changed)
			addon = xbmcaddon.Addon()

			# host and port from "settings.xml"
			self.host = addon.getSetting("gateway.ip-address")
			self.port = int(addon.getSetting("gateway.port"))

			# Connect. (function inherited from class 'TCPDaemon')
			self.tcp_ip_socket.reroute_connection(self.host, self.port)

			# send 'connect'
			self.tcp_ip_socket.send_buffer(CONNECT)

			xbmc.log("%s: %s - launching TCP/IP socket. (start asyncore loop)" % (__addonid__, self.__class__.__name__), xbmc.LOGDEBUG)

			# inherited from 'TCPDaemon' class (blocking function)
			self.tcp_ip_socket.start()

			xbmc.log("%s: %s - connection lost. (exit asyncore loop)" % (__addonid__, self.__class__.__name__), xbmc.LOGINFO)

		# the loop exited
		xbmc.log("%s: %s - service main loop stopped (function returns, thread terminates)." % (__addonid__, self.__class__.__name__), level=xbmc.LOGDEBUG)


# a separate class of 'ping-daemon'
class PingDaemon(object):

	def __init__(self, tcp_ip_socket):

		# socket instance
		self.tcp_ip_socket = tcp_ip_socket

		# counter for ping thread.
		self.pings_rx = 0
		self.pings_tx = 0
		self.ping_rx_timestamp = time.time()

	# request to start the ping daemon
	def start(self):

		# reset ping counters (if a restart occured)
		self.pings_rx = 0
		self.pings_tx = 0

		# launch new thread
		thread = Thread(name='PingDaemon', target=self._ping_daemon)
		thread.daemon = True
		thread.start()

	# runs in a separate thread
	def _ping_daemon(self):

		# log
		xbmc.log("%s: %s - starting ping daemon." % (__addonid__, self.__class__.__name__), xbmc.LOGDEBUG)

		# loop while still connected and until abort is requested from XBMC/KODI
		while self.tcp_ip_socket.is_connected() and not __monitor__.abortRequested():

			self.tx_ping()
			time.sleep(PING_TIME_INTERVAL)

		# log
		xbmc.log("%s: %s - terminating ping daemon (function returns)." % (__addonid__, self.__class__.__name__), xbmc.LOGDEBUG)

	# received ping
	def rx_ping(self):

		#xbmc.log("%s: %s - receiving ping (number: %s, last received: %.1f [s] ago )" % (__addonid__, self.__class__.__name__, self.pings_rx, (time.time() - self.ping_rx_timestamp)), xbmc.LOGDEBUG)

		# increase counter, capture timestamp
		self.pings_rx += 1
		self.ping_rx_timestamp = time.time()

	# transmit ping
	def tx_ping(self):

		# increase counter
		self.pings_tx += 1

		# send ping message
		self.tcp_ip_socket.send_buffer(PING)

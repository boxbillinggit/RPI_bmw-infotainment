__author__ = 'Lars'
# this module handles the overlay TCP protocol and functions

# TODO: rename module to "TCPIPHandler".
# TODO: restructure module (names, classes, and more)
# TODO: ibus meesage method 'data_packet' is a dead end.
# TODO: look over all loglevels -and log messages (decrease amount?)
# TODO: implement tx of IBUS-messages

# about loglevels:
# http://kodi.wiki/view/Log_file/Advanced#advancedsettings.xml_for_normal_debugging

# Python dev docs: http://mirrors.kodi.tv/docs/python-docs/14.x-helix/
import xbmc, xbmcplugin, xbmcgui, xbmcaddon

__monitor__ 	= xbmc.Monitor()
__addon__		= xbmcaddon.Addon()
__addonname__	= __addon__.getAddonInfo('name')
__addonid__		= __addon__.getAddonInfo('id')

# import all libraries
import time
import settings
from threading import Thread
from TCPdaemon import TCPIPSocketAsyncore
from keymap import KeyMap

# TCP/IP protocol settings
HEADER_LENGTH = 8
PING_TIME_INTERVAL = 3		# seconds

# adjust header to correct length (8byte)
def _resize_header(data):
	return data + ([0] * (HEADER_LENGTH - len(data)))

# TCP protocol headers. (also resize header to 8byte)
PING 		= _resize_header([0xAA, 0xAA])
CONNECT 	= _resize_header([0x68, 0x69])	# ASCII: 'hi'
DISCONNECT 	= _resize_header([])
REROUTE 	= [0x63, 0x74]					# ASCII: 'ct'

# static methods

def rx_ibus_frame(src, dst, data):
	xbmc.log("%s: TODO: parse IBUS message." % __addonid__, xbmc.LOGDEBUG)


# rx errors
def rx_err_frame_length():
	xbmc.log("%s: No length on TCP/IP frame" % __addonid__, xbmc.LOGDEBUG)


def rx_err_data_length():
	xbmc.log("%s - Unexpected rx data length." % __addonid__, xbmc.LOGERROR)


def rx_err_header_content(buf):
	xbmc.log('%s - Unexpected rx header content. [%s]' % (__addonid__, str(buf).encode('hex')), xbmc.LOGERROR)


# Base class handler for the TCP protocol. Main point for routing Rx -and Tx data.
class TCPIPHandler(object):

	# init the class
	def __init__(self):

		# data for handling the TCP/IP frame
		self.awaiting_data_chunk = False
		self.dst = None
		self.src = None
		self.len_data = None

		# init TCP/IP-socket
		self.tcp_ip_socket = TCPIPSocketAsyncore()
		self.tcp_ip_socket.handle_message = self.rx_tcp_ip_frame

		# init TCP/IP-daemon
		self.tcp_ip_daemon = TCPIPDaemon(self.tcp_ip_socket)
		self.start = self.tcp_ip_daemon.start
		self.stop = self.tcp_ip_daemon.stop

		# init ping transmitter
		self.ping_daemon = PingDaemon(self.tcp_ip_socket)

		xbmc.log("%s: %s - init class." % (__addonid__, self.__class__.__name__), xbmc.LOGDEBUG)

	# Main function for handling the received TCP/IP frames.
	def rx_tcp_ip_frame(self, rx):

		"""
		We have 3 cases:

		 * header has no length: disconnect message from OpenBM-daemon.
		 * header only (data length is zero): special overlay TCP/IP-protocol message.
		 * header+data: we have a IBUS message to parse (data frame can be transmitted in next TCP/IP frame though).
		"""

		# TCP/IP frame length
		length = len(rx)

		if not length:
			# empty TCP/IP frame received.
			rx_err_frame_length()

		elif length and not (rx[2] or self.awaiting_data_chunk):
			# received header only (data length is zero, header is not received in previous TCP/IP-frame)
			self.rx_header_only(rx)

		else:
			# received header+data.
			self.rx_header_and_data(rx)

	# Header only. Handle the special overlay TCP/IP-protocol message.
	def rx_header_only(self, rx):

		if bytearray(REROUTE) in rx:

			# reform to base-16 (not very easy though)
			_rx = map(chr, rx)
			_port = int((_rx[5]+_rx[4]).encode('hex'), 16)

			# close connection...
			self.tcp_ip_socket.close()

			# ...and reroute to new port!
			self.tcp_ip_socket.reroute_connection(self.tcp_ip_daemon.host, _port)

			# start a ping thread.
			self.ping_daemon.start()

		elif bytearray(PING) == rx:
			self.ping_daemon.rx_ping()

		else:
			rx_err_header_content(rx)

	# Parse TCP/IP frame
	def rx_header_and_data(self, rx):

		# this is type 'bytearray'
		length = len(rx)
		len_data = rx[2]

		# header is already received, this TCP/IP frame contains the data packet.
		if self.awaiting_data_chunk:

			# Check if length is as expected
			if length == self.len_data:

				# use src and dst stored from previous received header.
				rx_ibus_frame(self.src, self.dst, rx)

			else:
				rx_err_data_length()

			# reset flag
			self.awaiting_data_chunk = False

		# header+data in current TCP frame
		elif len_data and length == (HEADER_LENGTH + len_data):

			INDEX = (HEADER_LENGTH-1)

			# data is located after the header
			data = rx[INDEX:]
			self.src = rx[0]
			self.dst = rx[1]
			self.len_data = rx[2]

			rx_ibus_frame(self.src, self.dst, data)

		# header received. data will be sent next TCP/IP-frame
		elif len_data and (length < (HEADER_LENGTH + len_data)):

			# save dst and src until data packet is received
			self.src = rx[0]
			self.dst = rx[1]
			self.len_data = rx[2]

			# set flag awaiting data
			self.awaiting_data_chunk = True

		# some error occured
		else:
			rx_err_data_length()

			# clear flag (some error occured)
			self.awaiting_data_chunk = False


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

"""
This module handles the overlay TCP/IP-protocol for communicating with gateway.
"""

# TODO: avoid data conversions, use bytearray or string here in this module???

import log as log_module

log = log_module.init_logger(__name__)
__author__ = 'lars'

HEADER_SIZE = 8
SRC = 0
DST = 1
LEN = 2


def hexstring(bytes):

	"""
	Convert bytes to a hexstring.
	"""

	return " ".join(map(lambda byte: hex(byte), bytes))


def create_header(content):

	"""
	create a header with correct length (8byte).
	"""

	data = list(content)
	header = data + ([0] * (HEADER_SIZE - len(data))) if len(data) < 8 else data[:8]

	return bytearray(header)


def create_frame(msg):

	"""
	Create TCP/IP-frame from 3-tuple: ([src], [dst], [data])
	"""

	src, dst, data = msg

	# create header and insert length
	header = create_header(src+dst)
	header[2] = len(data)

	return header+bytearray(data)


def create_signal(data):

	"""
	Create 3-tuple signal from TCP/IP-frame. Frame must have length as expected

	("src", "dst", "data")
	"""

	return hex(data[SRC]), hex(data[DST]), hexstring(data[HEADER_SIZE:])


def is_length_valid(data):

	"""
	is length valid?
	"""

	return True if len(data) >= get_expected_length(data) else False


def is_header_only(data):

	"""
	Is this a header with no length?
	"""

	return True if get_expected_length(data) == HEADER_SIZE and is_length_valid(data) else False


def is_header_and_data(data):

	"""
	Is this a complete DATA+HEADER ?
	"""

	return True if not is_header_only(data) and is_length_valid(data) else False


def get_expected_length(data):

	"""
	Return total expected length of complete HEADER + DATA (if byte for length exists)
	"""

	return (data[LEN] + HEADER_SIZE) if (len(data) >= LEN) else None


def get_slice(data):

	"""
	return current slice (if length is valid).
	"""

	length = get_expected_length(data)

	return data[:length] if length and is_length_valid(data) else None


def get_port(header):

	"""
	Get port number from rerouting-request HEADER.
	"""

	return int(header[5] << 8) + header[4]


class Protocol(object):

	"""
	This class handles the raw bytes from socket and returns the BUS-signals only.
	"""

	PING 		= create_header("\xaa\xaa")
	CONNECT 	= create_header("hi")
	DISCONNECT 	= create_header("")
	REROUTE 	= bytearray("ct")

	def __init__(self):
		self.buffer = bytearray()
		self.errors = 0

	def handle_data(self, data):

		"""
		Main method for handling received TCP/IP-buffer.

		Parses out HEADER and DATA frames. if "HEADER" is received but not DATA
		we put this header in the buffer until next received data.

		if parse loop has finished with remaining data above 8bytes, we flush the
		buffer since the buffer did not contain a complete header+data.
		"""

		if type(data) is not bytearray:
			raise TypeError("data must be of type 'bytearray'")

		index = 0
		signals = []
		recvbuffer = self.buffer + data

		while index < len(recvbuffer):

			chunk = recvbuffer[index:]

			if is_header_and_data(chunk):
				signal = get_slice(chunk)
				index += len(signal)
				signals.append(create_signal(signal))
				continue

			elif is_header_only(chunk):
				header = get_slice(chunk)

				if self.handle_header(header):
					index += len(header)
					continue
				else:
					self.handle_error(header)
					return signals

			break

		remaining_data = recvbuffer[index:]

		if len(remaining_data) > HEADER_SIZE:
			self.handle_error(remaining_data)
		else:
			self.buffer = remaining_data

		return signals

	def handle_error(self, data):

		"""
		Called when unknown data is received -or allocated in the buffer.
		"""

		del self.buffer[:]
		self.errors += 1
		log.debug("unexpected frame: {} (error count: {})".format(log_module.hexstring(data), self.errors))

	def handle_header(self, header):

		"""
		Select action dependent on content in header, then return "True".
		"""

		if Protocol.REROUTE in header:
			self.handle_reroute(get_port(header))

		elif Protocol.PING == header:
			self.handle_ping()

		else:
			return False

		return True

	def handle_ping(self):
		"""
		overridden in subclass.
		"""
		pass

	def handle_reroute(self, port):
		"""
		overridden in subclass.
		"""
		pass

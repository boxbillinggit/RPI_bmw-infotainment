from unittest import TestCase
import gateway_protocol
import signaldb

Protocol = gateway_protocol.Protocol

__author__ = 'lars'


def reroute_to_port(port):

	"""
	Create header for a reroute-request.
	"""

	data = gateway_protocol.create_header(Protocol.REROUTE)

	# insert port
	data[4] = port & 0xFF
	data[5] = port >> 8 & 0xFF

	return data


class GatewayProtocol(gateway_protocol.Protocol):

	"""
	Subclass with implemented methods for reroute -and ping.
	"""

	def __init__(self):
		super(GatewayProtocol, self).__init__()
		self.ping = False
		self.reroute_to = None

	def reset_states(self):
		self.ping = False
		self.reroute_to = None
		self.errors = 0

	def handle_ping(self):
		self.ping = True

	def handle_reroute(self, port):
		self.reroute_to = port

protocol = GatewayProtocol()

SIGNAL = signaldb.create(("IBUS_DEV_BMBT", "IBUS_DEV_CDC", "source.push"))


class TestProtocol(TestCase):

	def setUp(self):
		pass

	def tearDown(self):
		protocol.reset_states()

	def test_ping(self):

		"""
		Test action for receiving a ping, expecting callback "handle_ping()"
		"""

		recv = protocol.handle_data(Protocol.PING)
		self.assertEqual(len(recv), 0)
		self.assertTrue(protocol.ping)

	def test_reroute(self):

		"""
		Test action for receiving a reroute request, expecting callback
		"handle_reroute()" with a port as argument.
		"""

		port = 1234
		send = reroute_to_port(port)
		recv = protocol.handle_data(send)
		self.assertEqual(len(recv), 0)
		self.assertEqual(port, protocol.reroute_to)

	def test_unknown_header(self):

		"""
		header with zero length and unknown content
		"""

		send = bytearray([0]*8)
		recv = protocol.handle_data(send)
		self.assertEqual(len(recv), 0)
		self.assertEqual(len(protocol.buffer), 0)
		self.assertEqual(protocol.errors, 1)

	def test_one_complete_frame(self):

		"""
		One complete frame of header+data is sent.
		"""

		send = gateway_protocol.create_frame(SIGNAL)
		recv = protocol.handle_data(send)
		self.assertEqual(len(recv), 1)
		self.assertEqual(SIGNAL, recv[0])
		self.assertEqual(len(protocol.buffer), 0)

	def test_multiple_complete_frames(self):

		"""

		"""

		send = gateway_protocol.create_frame(SIGNAL)*6
		recv = protocol.handle_data(send)
		self.assertEqual(len(recv), 6)
		self.assertEqual(len(protocol.buffer), 0)

		for index, recv_signal in enumerate(recv):
			self.assertEqual(recv_signal, recv[index])

	def test_one_frame_sliced(self):

		"""
		header and data is sent in separate frames.
		"""

		send = gateway_protocol.create_frame(SIGNAL)
		recv_none = protocol.handle_data(send[:gateway_protocol.HEADER_SIZE])
		self.assertEqual(len(recv_none), 0)
		recv = protocol.handle_data(send[gateway_protocol.HEADER_SIZE:])
		self.assertEqual(len(recv), 1)
		self.assertEqual(SIGNAL, recv[0])
		self.assertEqual(len(protocol.buffer), 0)

	def test_mixed_valid_frames(self):

		"""
		send some mixed data containing frames along with ping and reroute, etc..
		"""

		send = \
			gateway_protocol.create_frame(SIGNAL)*2 + \
			Protocol.PING + \
			gateway_protocol.create_frame(SIGNAL)*2 + \
			reroute_to_port(1234)

		recv = protocol.handle_data(send)
		self.assertEqual(len(recv), 4)
		self.assertEqual(len(protocol.buffer), 0)
		self.assertTrue(protocol.ping)
		self.assertIsNotNone(protocol.reroute_to)
		for index, recv_signal in enumerate(recv):
			self.assertEqual(recv_signal, recv[index])

	def test_mixed_valid_frames_sliced(self):

		"""
		send some mixed data containing frames along with ping and reroute, etc..
		but in slices..
		"""

		send = \
			gateway_protocol.create_frame(SIGNAL)*2 + \
			Protocol.PING + \
			gateway_protocol.create_frame(SIGNAL)*2 + \
			reroute_to_port(1234)

		recv = []
		half = len(send) / 2
		recv.extend(protocol.handle_data(send[:half]))
		recv.extend(protocol.handle_data(send[half:]))

		self.assertEqual(len(recv), 4)
		self.assertEqual(len(protocol.buffer), 0)
		self.assertTrue(protocol.ping)
		self.assertIsNotNone(protocol.reroute_to)
		for index, recv_signal in enumerate(recv):
			self.assertEqual(recv_signal, recv[index])

	def test_frame_not_valid(self):

		"""
		a chunk of not valid data is sent.

		buffer is expected to be flushed, empty list expected to be returned.
		"""

		send = bytearray([0xFF]*14)
		# self.assertRaises(gateway_protocol.RecvError, protocol.handle_data, send)
		recv = protocol.handle_data(send)
		self.assertEqual(protocol.errors, 1)
		self.assertEqual(len(recv), 0)
		self.assertEqual(len(protocol.buffer), 0)

	def test_sliced_frame_not_valid(self):

		"""
		first part sent could be a potential header (8bytes).
		last part sent will raise a error, since header+data was not taken care of..

		buffer is expected to be flushed.
		"""

		send = bytearray([0xFF]*8)
		recv = protocol.handle_data(send)
		self.assertEqual(len(recv), 0)
		recv = protocol.handle_data(send)
		# self.assertRaises(gateway_protocol.RecvError, protocol.handle_data, send)
		self.assertEqual(protocol.errors, 1)
		self.assertEqual(len(recv), 0)
		self.assertEqual(len(protocol.buffer), 0)

	def test_valid_frame_beginning_with_invalid_data(self):

		"""
		Expecting to rasise error and flush buffer.. and not return any signals..
		"""

		send = \
			bytearray([0xFF]*14) + \
			gateway_protocol.create_frame(SIGNAL)

		# self.assertRaises(gateway_protocol.RecvError, protocol.handle_data, send)
		recv = protocol.handle_data(send)
		self.assertEqual(protocol.errors, 1)
		self.assertEqual(len(recv), 0)
		self.assertEqual(len(protocol.buffer), 0)

	def test_valid_frame_ending_with_invalid_data(self):

		"""
		Expecting to return the parsed frames until invalid data occurs.
		"""

		send = gateway_protocol.create_frame(SIGNAL)*3 + \
			bytearray([0xFF]*14)
		recv = protocol.handle_data(send)

		# self.assertRaises()
		self.assertEqual(len(recv), 3)
		self.assertEqual(len(protocol.buffer), 0)
		self.assertEqual(SIGNAL, recv[0])
		self.assertEqual(protocol.errors, 1)

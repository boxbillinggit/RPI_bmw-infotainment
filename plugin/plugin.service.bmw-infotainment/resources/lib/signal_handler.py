"""
This module handles received BUS-signals.
"""

import re
import system
import event_handler
import log as log_module
import bmw
import bmbt

import signal_recorder

log = log_module.init_logger(__name__)
__author__ = 'lars'


def check_if_data_matches(string, pattern):

	""" Find exact match for DATA by evaluating with regular expression. """

	res = re.match("{}$".format(pattern), string)

	return res.groups() if res else None


def match_found(bus_sig, event_sig):

	"""
	Return tuple (empty or filled) if a match between received signal and an event is found,
	else return "None"

	"None" in SRC or DST means match all (don't evaluate), but data must always exist and be
	equal!
	"""

	src, dst, data = event_sig
	bus_src, bus_dst, bus_data = bus_sig

	if not data:
		raise AttributeError("Data must not be empty or None")

	devices_matches = (
		(not src or bus_src == src) and
		(not dst or bus_dst == dst)
	)

	return None if not devices_matches else check_if_data_matches(bus_data, data)


class Events(object):

	"""
	Callbacks to be triggered from a received signal. also containing
	methods for to dynamically update, add -or remove events at runtime.
	"""

	INDEX, SIGNAL, METHOD, ARGS, KWARGS = range(5)

	def __init__(self, send):

		self.send = send
		self.events = []
		self.index = 0

		# devices
		self.cd_changer = bmw.CDChanger(send)
		self.kombi_instrument = bmw.KombiInstrument(send)
		self.bmbt_monitor = bmbt.Monitor(send)

	def inc_idx(self):

		self.index += 1
		return self.index

	def initialize_events(self):

		""" Initial events launched when system is just started (called from service.py) """

		components = (system, signal_recorder, self.kombi_instrument, self.cd_changer, self.bmbt_monitor)

		for component in components:

			component.init_events(self.bind_event)

	def bind_event(self, signal, method, *args, **kwargs):

		"""	Add one event to list. if keyword argument "static=False" is used, event will
		be deleted from list after execution (one-time event) """

		index = self.inc_idx()
		item = (index, signal, method, args, kwargs)

		self.events.append(item)
		return index

	def unbind_event(self, ref):

		""" Remove one event, with index as reference. """

		for item in self.events:

			index = item[Events.INDEX]

			if index == ref:
				self.events.remove(item)
				return index


class SignalHandler(Events):

	"""	Interface implementing callbacks and methods for bus-signals. """

	def __init__(self, handle_send):
		self.handle_send = handle_send
		Events.__init__(self, self.send)

	def send(self, signal, *args, **kwargs):

		"""	Use event-handler for sending since "handle_send is directly refereed down to
		socket (could maybe be blocking, etc). """

		event_handler.add(self.handle_send, signal, *args, **kwargs)

	def receive(self, signal):

		"""
		Received a bus signal, filter against matching event, can use regular expressions.
		Matched regexp defined in group will be forwarded to method as *args,  along with
		*args and **kwargs provided from event-binding.

		Callback from ThreadedSocket-thread, transfer task to EventHandler-thread instead.

		Signal is 3-tuple: (src, dst, data)
		"""

		for item in self.events:

			index, _signal, method, args, kwargs = item

			match = match_found(signal, _signal)

			if match is not None:

				if not kwargs.pop("static", True):
					self.events.remove(item)

				event_handler.add(method, *(args+match), **kwargs)
				# log.debug("{} - match for signal: {}".format(self.__class__.__name__, log_module.pritty_hex(signal)))

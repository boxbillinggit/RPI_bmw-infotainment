"""
This module handles received BUS-signals.
"""

import re

import event_handler
import log as log_module
from signal_events import Events

log = log_module.init_logger(__name__)
__author__ = 'lars'


def check_if_data_matches(string, pattern):

	"""
	Find exact match for DATA by evaluating with regular expression.
	"""

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


class SignalHandler(Events):

	"""
	Interface implementing callbacks and methods for bus-signals.
	"""

	def __init__(self, send):
		Events.__init__(self, send)

	def receive(self, recvd_signal):

		"""
		Received a bus signal, filter against matching event, can use regular expressions.
		Matched regexp defined in group will be forwarded to method as *args,  along with
		*args and **kwargs provided from event-binding.

		Signal is 3-tuple: (src, dst, data)
		"""

		for item in self.events:

			index, signal, method, args, kwargs = item

			match = match_found(recvd_signal, signal)

			if match is not None:

				if not kwargs.pop("static", True):
					self.events.remove(item)

				event_handler.add(method, *(match+args), **kwargs)
				log.debug("{} - match for signal: {}".format(self.__class__.__name__, log_module.pritty_hex(recvd_signal)))

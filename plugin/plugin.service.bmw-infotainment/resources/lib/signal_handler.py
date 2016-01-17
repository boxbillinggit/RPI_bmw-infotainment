"""
This module handles received BUS-signals.
"""

import re

from signal_events import Events
import event_handler
import log as log_module

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


class Filter(object):

	"""
	Main class for this module. Filter BUS-messages to a matching event (if defined)
	"""

	def __init__(self):

		self.events = Events()

	def handle_signal(self, recvd_signal):

		"""
		Handles bus signals received from TCP/IP socket. Check if we have a matching
		event. If match found, put task on event queue but don't stop searching (could
		be more events when using regexp, etc..).

		Forward data from regexp (if that data exists), along with args and kwargs
		provided from binding event.

		Signal is 3-tuple: (src, dst, data)
		"""

		for item in self.events.list:

			index, signal, method, args, kwargs = item

			match = match_found(recvd_signal, signal)

			if match is not None:

				if not kwargs.pop("static", True):
					self.events.list.remove(item)

				event_handler.add(method, *(match+args), **kwargs)
				log.debug("{} - match for signal: {}".format(self.__class__.__name__, log_module.pritty_hex(recvd_signal)))

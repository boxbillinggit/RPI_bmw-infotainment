"""
This module handles received BUS-signals.
"""

import re

from signal_events import Events
from event_handler import Scheduler
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

		self.scheduler = Scheduler()
		self.events = Events(self.scheduler)

	def handle_signal(self, bus_sig):

		"""
		Handles bus signals received from TCP/IP socket. Check if we have a matching
		event. If match found, put task on event queue and stop searching.

		Forward data from regexp as *args (if that data exists).

		Signal is 3-tuple: (src, dst, data)
		"""

		for index, event_sig, event in self.events.list:

			match = match_found(bus_sig, event_sig)

			if match is not None:
				self.scheduler.add(event, *match)
				log.debug("{} - match for signal: {}".format(self.__class__.__name__, log_module.pritty_hex(bus_sig)))
				break

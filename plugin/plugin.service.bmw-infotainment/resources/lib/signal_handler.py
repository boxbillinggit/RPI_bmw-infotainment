"""
This module handles received BUS-signals.
"""

from signal_events import Events
from event_handler import EventHandler
import log as log_module
log = log_module.init_logger(__name__)

__author__ = 'lars'


def match_found(bus_sig, event_sig):

	"""
	Return "True" if a match between received signal and an event is found.

	"None" means match all (don't evaluate), but data must exist and be equal!
	"""

	src, dst, data = event_sig
	bus_src, bus_dst, bus_data = bus_sig

	return not (
		(src and bus_src != src) or
		(dst and bus_dst != dst) or
		(bus_data != data)
	)


class Filter(object):

	"""
	Main class for this module. Filter BUS-messages to a matching event (if defined)
	"""

	def __init__(self, queue=None):

		self.queue = queue or EventHandler.Queue
		self.events = Events(self.queue)

	def handle_signal(self, bus_sig):

		"""
		Handles bus signals received from TCP/IP socket. Compare if we have a matching
		event. If match found, put task on event queue (None=scheduled to execute now)
		and stop searching.

		Signal is 3-tuple: (src, dst, data)
		"""

		src, dst, data = bus_sig

		for index, event_sig, event in self.events.list:

			if match_found(bus_sig, event_sig):
				self.queue.put((event, None))
				log.debug("{} - match for signal {}".format(self.__class__.__name__, log_module.hexstring(src+dst+data)))
				break

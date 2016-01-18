import signaldb as sdb

__author__ = 'lars'

SRC = "IBUS_DEV_CDC"


def hexstring(string):

	""" converts a string to hexstring"""

	return " ".join(map(lambda char: "{:#x}".format(ord(char)), string))


class KombiInstrument(object):

	DISPLAY_SIZE = 20

	def __init__(self, send, signal_filter):
		self.send = send
		self.signal_filter = signal_filter

	@staticmethod
	def format_text(raw_text):

		size = KombiInstrument.DISPLAY_SIZE
		text = raw_text[:size] + " " * (size - len(raw_text[:size]))

		return hexstring(text)

	def write_text(self, text):

		""" Write text to kombiinstrument-display! """

		self.send(sdb.create((SRC, "IBUS_DEV_IKE", "ike-text.normal"), TEXT=self.format_text(text)))

	def welcome_text(self, text):

		"""
		Show welcome-text only if ignition is on. Send ignition-status request and
		set callback for ignition-status on.
		"""

		self.signal_filter.bind_event(sdb.create(("IBUS_DEV_IKE", "IBUS_DEV_GLO", "ign-key.on")), self.write_text, text, static=False)
		self.send(sdb.create((SRC, "IBUS_DEV_IKE", "ign-key.req-state")))

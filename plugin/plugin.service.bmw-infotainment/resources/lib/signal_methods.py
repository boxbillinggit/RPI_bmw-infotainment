import signaldb

__author__ = 'lars'

SRC = "IBUS_DEV_CDC"


def hexstring(string):

	""" converts a string to hexstring"""

	return " ".join(map(lambda char: "{:#x}".format(ord(char)), string))


class KombiInstrument(object):

	DISPLAY_SIZE = 20

	def __init__(self, send):
		self.send = send

	@staticmethod
	def format_text(raw_text):

		size = KombiInstrument.DISPLAY_SIZE
		text = raw_text[:size] + " " * (size - len(raw_text[:size]))

		return hexstring(text)

	def set_text(self, text):
		self.send(signaldb.create((SRC, "IBUS_DEV_IKE", "ike-text.normal"), TEXT=self.format_text(text)))

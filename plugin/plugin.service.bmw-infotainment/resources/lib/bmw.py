import signaldb

__author__ = 'lars'

EMULATED_IBUS_DEV = "IBUS_DEV_CDC"


class KombiInstrument(object):

	DEVICE 		 = "IBUS_DEV_IKE"
	DISPLAY_SIZE = 20

	def __init__(self, send):
		self.send = send

	@staticmethod
	def _format_text(raw_text):

		""" adjust size and convert to hex-string """

		size = KombiInstrument.DISPLAY_SIZE
		text = raw_text[:size] + " " * (size - len(raw_text[:size]))

		return signaldb.hex_string(text)

	def write_to_display(self, text):

		""" Write text to kombiinstrument-display! """

		self.send(signaldb.create((EMULATED_IBUS_DEV, self.DEVICE, "ike-text.normal"), TEXT=self._format_text(text)))

	def request_ign_state(self):

		""" Request current ign-state """

		self.send(signaldb.create((EMULATED_IBUS_DEV, self.DEVICE, "ign-key.req-sts")))

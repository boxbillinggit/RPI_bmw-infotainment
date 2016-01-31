import signaldb
import event_handler
from kodi import addon_settings
from tcp_events import State

__author__ = 'lars'

EMULATED_IBUS_DEV = "IBUS_DEV_CDC"


class KombiInstrument(object):

	"""
	Class for methods related to kombi-instrument.
	"""

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

	def init_events(self, bind_event):

		"""
		Show welcome-text only if ignition is on. Request ignition-status and
		set callback for ignition-status on.
		"""

		text = addon_settings.get_welcome_text()

		if not text:
			return

		# TODO how to handle welcome-message when other messages also pop's up in IKE during ignition on?
		bind_event(signaldb.create((KombiInstrument.DEVICE, "IBUS_DEV_GLO", "ign-key.on")), self.write_to_display, text, static=False)
		self.request_ign_state()

	def write_to_display(self, text):

		""" Write text to kombiinstrument-display! """

		self.send(signaldb.create((EMULATED_IBUS_DEV, self.DEVICE, "ike-text.normal"), TEXT=self._format_text(text)))

	def request_ign_state(self):

		""" Request current ign-state """

		self.send(signaldb.create((EMULATED_IBUS_DEV, self.DEVICE, "ign-key.req-sts")))


class CDChanger(object):

	"""
	Class for emulating CD-changer so radio get happy.
	"""

	DEVICE 		= "IBUS_DEV_CDC"
	INTERVAL 	= 8

	def __init__(self, send):
		self.send = send
		self.acknowledged = False

		self.disc = 0
		self.track = 0
		self.response = {}

	def init_events(self, bind_event):

		""" Events for the CD-changer emulation """

		src, dst = "IBUS_DEV_RAD", "IBUS_DEV_CDC"

		regexp = "[0-9]"

		# poll handling
		event_handler.add(self.broadcast, interval=self.INTERVAL)
		bind_event(signaldb.create((src, dst, "device.poll")), self.poll_response)

		# emulated responses
		bind_event(signaldb.create((src, dst, "cd-changer.req-status")), self.respond, "status")
		bind_event(signaldb.create((src, dst, "cd-changer.req-stop")), self.respond, "stop")
		bind_event(signaldb.create((src, dst, "cd-changer.req-play")), self.respond, "play")
		bind_event(signaldb.create((src, dst, "cd-changer.req-fast-scan"), DIRECTION=regexp), self.respond, "fast-scan")
		bind_event(signaldb.create((src, dst, "cd-changer.req-change-cd"), DISC=regexp), self.respond, "change-cd")
		bind_event(signaldb.create((src, dst, "cd-changer.req-scan"), DIRECTION=regexp), self.respond, "scan")
		bind_event(signaldb.create((src, dst, "cd-changer.req-random"), STATE=regexp), self.respond, "random")
		bind_event(signaldb.create((src, dst, "cd-changer.req-change-track"), DIRECTION=regexp), self.respond, "change-track")

		self.response = {
			"status": "cd-changer.sts-stopped",
			"stop": "cd-changer.sts-stopped",
			"play": "cd-changer.sts-playing",
			"change-track": "cd-changer.sts-start-playing",
			# "": "cd-changer.sts-fast-scan-forward",
			# "": "cd-changer.sts-fast-scan-backward",
			# "": "cd-changer.sts-track-end",
			"change-cd": "cd-changer.sts-cd-seek"
		}

	def poll_response(self):

		""" Reply on poll, stop broadcasting """

		self.acknowledged = True
		self.send(signaldb.create((self.DEVICE, "IBUS_DEV_LOC", "device.ready")))

	def broadcast(self):

		""" periodically broadcast until poll is answered """

		if self.acknowledged:
			return False

		if State.CurrentState == State.CONNECTED:
			self.send(signaldb.create((self.DEVICE, "IBUS_DEV_LOC", "device.broadcast")))

		return True

	def respond(self, request):

		""" handle request and send response accordingly """

		src, dst = "IBUS_DEV_CDC", "IBUS_DEV_RAD"

		signal = self.response.get(request)

		if signal:
			self.send(signaldb.create((src, dst, signal), DISC=self.disc, TRACK=self.track))

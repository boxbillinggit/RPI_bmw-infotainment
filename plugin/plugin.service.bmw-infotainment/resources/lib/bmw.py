import event_handler
import kodi.builtin
import kodi.addon_settings
import time
from tcp_events import State
import signaldb as sdb
import log as log_module


log = log_module.init_logger(__name__)

__author__ = 'lars'


class KombiInstrument(object):

	DEVICE = "IBUS_DEV_IKE"

	DISPLAY_SIZE 		= 20
	MSG_DELAY_INIT 		= 3.0
	MSG_DELAY_OCCUPIED 	= 10.0

	def __init__(self, send):
		self.send = send

		self.welcome_msg = None
		self.last_msg = None
		self.msg_scheduled = False

	def init_events(self, bind_event):

		"""	Show welcome-text when ignition is turned on. If display is already occupied with a
		message, reschedule and display message later. Set callback for ignition-status on,
		then request current ignition-status."""

		bind_event(sdb.create(("IBUS_DEV_CCM", "IBUS_DEV_IKE", "ARBITRARY"), DATA=".*"), self.display_occupied)
		bind_event(sdb.create(("IBUS_DEV_IKE", "IBUS_DEV_GLO", "ign-key.on")), self.schedule_display_text, static=False)

		self.send(sdb.create(("IBUS_DEV_CDC", "IBUS_DEV_IKE", "ign-key.req-sts")))

	def display_occupied(self):

		self.last_msg = time.time()

		if self.msg_scheduled:
			event_handler.add(self.display_text, self.welcome_msg, timestamp=self.MSG_DELAY_OCCUPIED+self.last_msg, reschedule=True)

	def schedule_display_text(self):

		self.welcome_msg = kodi.addon_settings.get_welcome_text()

		if not self.welcome_msg:
			return

		if self.last_msg:
			timestamp = self.last_msg + self.MSG_DELAY_OCCUPIED
		else:
			timestamp = time.time() + self.MSG_DELAY_INIT

		self.msg_scheduled = True
		event_handler.add(self.display_text, self.welcome_msg, timestamp=timestamp)

	def display_text(self, text):

		size = KombiInstrument.DISPLAY_SIZE
		resized_text = text[:size] + " " * (size - len(text[:size]))

		self.msg_scheduled = False
		self.send(sdb.create(("IBUS_DEV_CDC", "IBUS_DEV_IKE", "ike-text.normal"), TEXT=sdb.hex_string(resized_text)))


class CDChanger(object):

	"""
	Class for emulating CD-changer so radio get happy.
	"""

	DEVICE   = "IBUS_DEV_CDC"
	INTERVAL = 8

	PLAYING, PAUSED, STOPPED = range(3)

	Response = {
		PLAYING: "cd-changer.playing",
		PAUSED:  "cd-changer.paused",
		STOPPED: "cd-changer.stopped",
	}

	TRACK_MIN, TRACK_MAX = (1, 255)
	DISC_MIN, DISC_MAX = (1, 6)

	def __init__(self, send):
		self.send = send
		self.acknowledged = False

		self.state = CDChanger.STOPPED
		self.disc = CDChanger.DISC_MIN
		self.track = CDChanger.TRACK_MIN

	def init_events(self, bind_event):

		""" Events for the CD-changer emulation """

		src, dst = "IBUS_DEV_RAD", "IBUS_DEV_CDC"

		regexp = "([0-9])"

		# poll handling
		event_handler.add(self.broadcast, interval=self.INTERVAL)
		bind_event(sdb.create((src, dst, "device.poll")), self.poll_response)

		# emulated responses
		bind_event(sdb.create((src, dst, "cd-changer.req-status")), self.handle_status)
		bind_event(sdb.create((src, dst, "cd-changer.req-stop")), self.handle_stop)
		bind_event(sdb.create((src, dst, "cd-changer.req-play")), self.handle_play)
		bind_event(sdb.create((src, dst, "cd-changer.req-pause")), self.handle_pause)
		bind_event(sdb.create((src, dst, "cd-changer.req-change-cd"), DISC=regexp), self.handle_change_cd)
		bind_event(sdb.create((src, dst, "cd-changer.req-change-track"), DIRECTION=regexp), self.handle_change_track)
		bind_event(sdb.create((src, dst, "cd-changer.req-random"), STATE=regexp), self.handle_random)
		# bind_event(sdb.create((src, dst, "cd-changer.req-fast-scan"), DIRECTION=regexp), self.respond, "fast-scan")
		# bind_event(sdb.create((src, dst, "cd-changer.req-scan"), DIRECTION=regexp), self.respond, "scan")

	def poll_response(self):

		""" Reply on poll, stop broadcasting """

		self.acknowledged = True
		self.send(sdb.create((self.DEVICE, "IBUS_DEV_LOC", "device.ready")))

	def broadcast(self):

		""" periodically broadcast until poll is answered """

		if self.acknowledged:
			return False

		if State.CurrentState == State.CONNECTED:
			self.send(sdb.create((self.DEVICE, "IBUS_DEV_LOC", "device.broadcast")))

		return True

	def handle_play(self):

		# Can't play if stopped, must have a playlist or similar as reference to play
		# kodi.builtin.media_player("Play")
		self.state = CDChanger.PLAYING
		self._respond(CDChanger.Response[self.state])

	def handle_stop(self):

		kodi.builtin.media_player("Stop")
		self.state = CDChanger.STOPPED
		self._respond(CDChanger.Response[self.state])

	def handle_pause(self):

		# Play is toggling. and we don't know current state
		# kodi.builtin.media_player("Play")
		self.state = CDChanger.PAUSED
		self._respond(CDChanger.Response[self.state])

	def handle_random(self, state):

		""" handle random-playing from original BMW UI """

		kodi.builtin.media_player(("RandomOn" if int(state) else "RandomOff"))

	def handle_scan(self):
		pass

	def handle_fast_scan(self):
		pass

	def handle_change_cd(self, disc):

		self.disc = int(disc)
		self.track = CDChanger.TRACK_MIN
		self._respond("cd-changer.seek-disc")
		self._respond("cd-changer.start-playing")

	def handle_status(self):

		self._respond(CDChanger.Response[self.state])

	def handle_change_track(self, direction):

		next_track = -1 if int(direction) else 1

		if CDChanger.TRACK_MIN <= (self.track+next_track) < CDChanger.TRACK_MAX:
			self.track += next_track

		self._respond("cd-changer.start-playing")

	def _respond(self, response):

		""" handle request and send response accordingly """

		src, dst = "IBUS_DEV_CDC", "IBUS_DEV_RAD"

		self.send(sdb.create((src, dst, response), DISC=self.disc, TRACK=self.track))
		log.debug("CDChanger responds with: {} (disc: {}, track: {})".format(response, self.disc, self.track))

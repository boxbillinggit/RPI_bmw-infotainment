import main_thread
import system
import kodi.builtin
import signaldb as sdb
import log as log_module

from kodi import gui
from buttons import Button

log = log_module.init_logger(__name__)


__author__ = 'lars'


def get_active_screens(bitmask):

	if not bitmask:
		return "None"

	states = []

	for idx, state in enumerate(Monitor.Screen):

		if bitmask & pow(2, idx):
			states.append(state)

	return ", ".join(states)


class Monitor(object):

	# higher number is suppressing states with lower numbers
	SCREEN_OFF = 0
	SCREEN_MEDIA, SCREEN_INFO, SCREEN_TONE, SCREEN_SELECT = map(lambda exp: pow(2, exp), range(4))
	Screen = ("SCREEN_MEDIA", "SCREEN_INFO", "SCREEN_TONE", "SCREEN_SELECT")

	Media = ("MEDIA_OFF", "MEDIA_CDC", "MEDIA_RADIO", "MEDIA_TAPE")
	MEDIA_OFF, MEDIA_CDC, MEDIA_RADIO, MEDIA_TAPE = range(4)

	def __init__(self, send):
		self.send = send

		self.current_screen = Monitor.SCREEN_OFF
		self.current_media = Monitor.MEDIA_OFF
		self.cdc_active = False

	def init_events(self, bind_event):

		self.init_controls(bind_event)

		src, dst = "IBUS_DEV_BMBT", "IBUS_DEV_RAD"

		# F0 05 FF 47 00 38 75 -> info push
		# F0 05 FF 47 00 0F 42 -> select push (to GLOBAL)
		# TODO: INFO is not detected for now (haven't found any good strategy for detecting "INFO" off)
		# bind_event(sdb.create((src, None, "info.push")),  self.set_screen, Monitor.SCREEN_INFO,  True)
		bind_event(sdb.create((src, dst, "tone.push")),   self.tone_or_select, Monitor.SCREEN_TONE)
		bind_event(sdb.create((src, None, "select.push")), self.tone_or_select, Monitor.SCREEN_SELECT)

		src, dst = "IBUS_DEV_RAD", "IBUS_DEV_GT"

		bind_event(sdb.create((src, dst, "screen.mainmenu")),   self.set_screen, Monitor.SCREEN_MEDIA,  False)
		bind_event(sdb.create((src, dst, "screen.current")),    self.set_screen, Monitor.SCREEN_MEDIA,  False)

		bind_event(sdb.create((src, dst, "screen.tone-off")),        self.tone_or_select, False)
		bind_event(sdb.create((src, dst, "screen.select-off")),      self.tone_or_select, False)
		bind_event(sdb.create((src, dst, "screen.tone-select-off")), self.tone_or_select, False)

		# available values for state RADIO: "FM", "FMD", "AM"
		regexp = ".* (?:{FM}|{AM}) .*".format(FM=sdb.hex_string("FM"), AM=sdb.hex_string("AM"))

		# rendering finished.
		# bind_event(sdb.create((src, dst, "index-area.refresh")), self.refresh_graphics)

		bind_event(sdb.create((src, dst, "index-area.write"), FIELD="1", TEXT=regexp), self.set_media_source, Monitor.MEDIA_RADIO)
		bind_event(sdb.create((src, dst, "text-area.upper"), LEFT=".*", MID=".*", RIGHT=sdb.hex_string("CD") + ".*"), self.set_media_source, Monitor.MEDIA_CDC)

		# TODO: "TAPE" and "OFF"

	def init_controls(self, bind_event):

		""" Initialize controls, etates, etc. """

		src, dst = "IBUS_DEV_BMBT", "IBUS_DEV_GT"

		right_knob = Button(hold=kodi.builtin.action("back"), release=kodi.builtin.action("Select"))
		bind_event(sdb.create((src, dst, "right-knob.push")),    self.ctrl_handler, right_knob.set_state_push)
		bind_event(sdb.create((src, dst, "right-knob.hold")),    self.ctrl_handler, right_knob.set_state_hold)
		bind_event(sdb.create((src, dst, "right-knob.release")), self.ctrl_handler, right_knob.set_state_release)

		bind_event(sdb.create((src, dst, "right-knob.turn-left"),  SCROLL_SPEED="([1-9])"), self.ctrl_handler, kodi.builtin.scroll("up"))
		bind_event(sdb.create((src, dst, "right-knob.turn-right"), SCROLL_SPEED="([1-9])"), self.ctrl_handler, kodi.builtin.scroll("down"))

		src, dst = "IBUS_DEV_BMBT", "IBUS_DEV_RAD"

		left = Button(push=kodi.builtin.action("Left"), hold=kodi.builtin.action("Left"))
		bind_event(sdb.create((src, dst, "left.push")),    self.ctrl_handler, left.set_state_push)
		bind_event(sdb.create((src, dst, "left.hold")),    self.ctrl_handler, left.set_state_hold)
		bind_event(sdb.create((src, dst, "left.release")), self.ctrl_handler, left.set_state_release)

		right = Button(push=kodi.builtin.action("Right"), hold=kodi.builtin.action("Right"))
		bind_event(sdb.create((src, dst, "right.push")),    self.ctrl_handler, right.set_state_push)
		bind_event(sdb.create((src, dst, "right.hold")),    self.ctrl_handler, right.set_state_hold)
		bind_event(sdb.create((src, dst, "right.release")), self.ctrl_handler, right.set_state_release)

		src, dst = "IBUS_DEV_BMBT", "IBUS_DEV_LOC"

		bind_event(sdb.create((src, None, "clock.push")), self.ctrl_handler, toggle_gui, gui.AddonOverview)

	def ctrl_handler(self, fcn, *args, **kwargs):

		""" Controls is active only if current state is correct """

		if self.cdc_active:
			fcn(*args, **kwargs)

	def set_media_source(self, source):

		""" Only one media source could be active """

		self.current_media = source
		self.set_screen(Monitor.SCREEN_MEDIA, True)

		log.debug("Current Media: {STATE}".format(STATE=Monitor.Media[self.current_media]))

	def tone_or_select(self, state):

		""" tone and select can only exist one at time (one closes the other, etc) """

		# clear bits first
		self.current_screen &= ~(Monitor.SCREEN_TONE | Monitor.SCREEN_SELECT)

		if state:
			self.current_screen |= state

		self.evaluate_screen()

	def set_screen(self, screen, active):

		""" current active screen changed """

		if active:
			self.current_screen |= screen
		else:
			self.current_screen &= ~screen

		self.evaluate_screen()

	def evaluate_screen(self):

		log.debug("Current Active Screen: {BITMASK} ({STATES})".format(BITMASK=bin(self.current_screen), STATES=get_active_screens(self.current_screen)))

		# if media is active, and no higher-priority screen is occupying, activate screen
		if self.current_screen & Monitor.SCREEN_MEDIA and self.current_screen <= Monitor.SCREEN_MEDIA and self.current_media == Monitor.MEDIA_CDC:
			self.state_cdc()
		else:
			self.state_not_cdc()

	def state_not_cdc(self):

		if not self.cdc_active:
			return

		log.debug("Screen off")

		self.cdc_active = False
		system.screen_off()
		open_gui(gui.DefaultScreen)

	def state_cdc(self):

		if self.cdc_active:
			return

		log.debug("Screen on")

		# removes CD-changer buttons TODO: does this work? (test using CDC as device also)
		self.send(sdb.create(("IBUS_DEV_RAD", "IBUS_DEV_GT", "index-area.refresh")))

		self.cdc_active = True
		gui.close_all_windows()
		system.screen_on()


def toggle_gui(WindowClass):

	""" Open or close a window """

	if close_gui(WindowClass):
		return

	open_gui(WindowClass)


def close_gui(WindowClass):

	""" Close a specific Window """

	win = gui.window_stack.pop(WindowClass.__name__, None)

	if not win:
		return False

	win.close()
	del win
	return True


def open_gui(WindowClass):

	""" close already open windows and open window, """

	# prevents flickering if we try opening a visible window.
	# if WindowClass.__name__ in gui.window_stack:
	# 	return

	gui.close_all_windows()
	main_thread.add(gui.open_window, WindowClass)

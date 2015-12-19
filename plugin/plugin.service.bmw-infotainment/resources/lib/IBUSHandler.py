"""
This module map events against IBUS-message
"""

import log as log_module
log = log_module.init_logger(__name__)

try:
	import xbmc, xbmcplugin, xbmcgui, xbmcaddon

except ImportError as err:
	log.warning("%s - using 'debug.XBMC'-modules instead" % err.message)
	import debug.xbmc as xbmc
	import debug.xbmcgui as xbmcgui
	import debug.xbmcaddon as xbmcaddon

__author__ 		= 'Lars'
__monitor__ 	= xbmc.Monitor()
__addon__		= xbmcaddon.Addon()
__addonname__	= __addon__.getAddonInfo('name')
__addonid__		= __addon__.getAddonInfo('id')
__addonpath__	= __addon__.getAddonInfo('path')


from BMButtons import Button
from TCPIPSocket import to_hexstr
import signaldb

#
# static methods
#




class Filter(object):

	"""
	This is the base class. This class handles -and route all IBUS-messages to it's events
	"""

	def __init__(self):

		# init event class
		self.event = Events()

		# init button states and it's actions
		self.button = Button()

		# init Signal-class (convert names to bytes)
		self.signal = signaldb.Signals()

		# init all events
		self.init_events()

	def init_events(self):

		# create namespaces for buttons: self.button.right_knob.push() -> this will trigger state 'push'.
		self.button.create(button="right_knob", states={"hold": self.event.execute("back"), "release": self.event.execute("enter")})
		self.button.create(button="right", states={"push": self.event.execute("right"), "hold": self.event.execute("right")})
		self.button.create(button="left", states={"push": self.event.execute("left"), "hold": self.event.execute("left")})

		# bind events to listeners
		self.event.bind(signal=self.signal.create({"src": "IBUS_DEV_BMBT", "data": "right-knob.push"}), event=self.button.right_knob.push)
		self.event.bind(signal=self.signal.create({"src": "IBUS_DEV_BMBT", "data": "right-knob.hold"}), event=self.button.right_knob.hold)
		self.event.bind(signal=self.signal.create({"src": "IBUS_DEV_BMBT", "data": "right-knob.release"}), event=self.button.right_knob.release)
		self.event.bind(signal=self.signal.create({"src": "IBUS_DEV_BMBT", "data": "right-knob.turn-left"}), event=self.event.execute("Up"))
		self.event.bind(signal=self.signal.create({"src": "IBUS_DEV_BMBT", "data": "right-knob.turn-right" }), event=self.event.execute("Down"))
		self.event.bind(signal=self.signal.create({"src": "IBUS_DEV_BMBT", "data": "left.push"}), event=self.button.left.push)
		self.event.bind(signal=self.signal.create({"src": "IBUS_DEV_BMBT", "data": "left.hold"}), event=self.button.left.hold)
		self.event.bind(signal=self.signal.create({"src": "IBUS_DEV_BMBT", "data": "left.release"}), event=self.button.left.release)
		self.event.bind(signal=self.signal.create({"src": "IBUS_DEV_BMBT", "data": "right.push"}), event=self.button.right.push)
		self.event.bind(signal=self.signal.create({"src": "IBUS_DEV_BMBT", "data": "right.hold"}), event=self.button.right.hold)
		self.event.bind(signal=self.signal.create({"src": "IBUS_DEV_BMBT", "data": "right.release"}), event=self.button.right.release)


	# TODO: make static method?
	def find_event(self, src, dst, data):

		# DEBUG
		log.debug("%s - receiving signal data: [%s]" % (self.__class__.__name__, to_hexstr(data)))

		# find a matching event
		for index, item in enumerate(self.event.map):

			# proceed if source is correct (don't evaluate empty items)
			if item.has_key('src') and item.get('src') != src:
				continue

			# proceed if destination is correct (don't evaluate empty items)
			if item.has_key('dst') and item.get('dst') != dst:
				continue

			# proceed if data is correct (don't evaluate empty items)
			if item.has_key('data') and item.get('data') != data:
				continue

			log.info("%s - found a event for received signal '%s'" % (self.__class__.__name__, item.get('description')))

			# We've found a match, stop looking and execute current action.
			execute_action = self.event.action[index]

			# execute action
			execute_action()

			# stop searching.
			break


class Events(object):

	"""
	This class implements all actions triggered by a IBUS-message

	Reference:
	http://kodi.wiki/view/keymap
	http://kodi.wiki/view/List_of_Built_In_Functions
	http://kodi.wiki/view/Action_IDs
	"""

	def __init__(self):
		self.map = list()
		self.action = list()

	def bind(self, signal, event):

		if len(self.map) == len(self.action):
			self.map.append(signal)
			self.action.append(event)
		else:
			log.error("%s - could not bind event for '%s'. due to unequal length" % (self.__class__.__name__, event.get('data')))

	# TODO: make static? rename to 'create()'
	def execute(self, arg):

		# return a function.
		return lambda: xbmc.executebuiltin("Action(%s)" % arg)


"""
This module map events against IBUS-message
"""

import log as logger
log = logger.init_logger(__name__)

try:
	import xbmc, xbmcplugin, xbmcgui, xbmcaddon

except ImportError as err:
	log.warning("%s - using 'debug.XBMC'-modules instead" % err.message)
	import debug.XBMC as xbmc
	import debug.XBMCGUI as xbmcgui
	import debug.XBMCADDON as xbmcaddon

__author__ 		= 'Lars'
__monitor__ 	= xbmc.Monitor()
__addon__		= xbmcaddon.Addon()
__addonname__	= __addon__.getAddonInfo('name')
__addonid__		= __addon__.getAddonInfo('id')
__addonpath__	= __addon__.getAddonInfo('path')

# ref: https://docs.python.org/2/library/xml.etree.elementtree.html
import xml.etree.ElementTree as ElementTree
import os

import settings
from BMButtons import Button
from TCPIPSocket import to_hexstr


# path settings (problem occurs else in XBMC/KODI)
SIGNAL_DB_PATH = os.path.join(__addonpath__, "resources", "data", settings.SIGNAL_DATABASE)


#
# static methods
#


def hexstr_to_int(str_buf):

	# create 'int' array from string
	return map(lambda str: int(str, 16), str_buf.split(" "))


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
		self.signal = Signals()

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


class Signals(object):

	"""
	Convert signals from name to bytes with help of the XML-database.
	"""

	def __init__(self):

		# read in the database
		tree = ElementTree.parse(SIGNAL_DB_PATH)

		# get root element
		self.root = tree.getroot()

	# create signal from descriptors
	def create(self, descriptor):

		# dictionary constructor
		signal = dict()

		if descriptor.get('src'):

			# translate 'source'
			signal['src'] = self._get_dev(descriptor.get('src'))

		if descriptor.get('dst'):

			# translate 'destination'
			signal['dst'] = self._get_dev(descriptor.get('dst'))

		# translate 'data'
		if descriptor.get('data'):

			signal['data'] = self._get_data(descriptor.get('data'))
			signal['description'] = descriptor.get('data')

		# return signal
		return signal

	def _get_dev(self, identifier):

		# find 'src' by id from XML-database
		src = self.root.findall("./MESSAGE/DEVICES/byte[@id='%s']" % identifier )

		if len(src) != 1:
			log.error("%s - %d item(s) found in XML-database for '%s'. Expecting one item" %(self.__class__.__name__, len(src), identifier))
			return None

		# convert to integer array. return the 'int' (not as list with only one single byte)
		byte_str = src[0].get('val')
		return hexstr_to_int(byte_str).pop()

	def _get_data(self, identifier):

		# get byte from XML-database.
		element_obj = self.root.findall("./MESSAGE/DATA/CATEGORY/byte[@id='%s']/.." % identifier )

		if len(element_obj) != 1:
			log.error("%s - %d reference(s) found in XML-database for '%s'. Expecting one reference" % (self.__class__.__name__, len(element_obj), identifier))
			return None

		# get the refereed byte for 'operation'
		operation_obj = self.root.findall("./MESSAGE/DATA/OPERATIONS/byte[@id='%s']" % element_obj[0].get('ref') )

		if len(operation_obj) != 1:
			log.error("%s - %d item(s) found in XML-database for '%s'. Expecting one item" % (self.__class__.__name__, len(operation_obj), identifier))
			return None

		operation = operation_obj[0].get('val')

		# get bytes from XML-database
		action_obj = element_obj[0].findall("byte[@id='%s']" % identifier)

		if len(action_obj) != 1:
			log.error("%s - %d item(s) found in XML-database for '%s'. Expecting one item" % (self.__class__.__name__, len(action_obj), identifier))
			return None

		action = action_obj[0].get('val')

		# finally - if no errors occured, merge arrays and return
		return bytearray(hexstr_to_int(operation) + hexstr_to_int(action))

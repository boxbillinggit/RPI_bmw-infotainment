__author__ = 'Lars'

#from keymap import States
try:
	# Python dev docs: http://mirrors.kodi.tv/docs/python-docs/14.x-helix/
	import xbmc, xbmcplugin, xbmcgui, xbmcaddon
	__addon__		= xbmcaddon.Addon()
	__addonid__		= __addon__.getAddonInfo('id')

except ImportError as err:
	print "WARNING: Failed to import XBMC/KODI modules."

# ref: https://docs.python.org/2/library/xml.etree.elementtree.html
import xml.etree.ElementTree as ElementTree
import os
import settings

# path settings (problem occurs else in XBMC/KODI)
BASE_LIB_PATH = os.path.join( os.getcwd(), "resources", "lib" )
SIGNAL_DB_PATH = os.path.join(BASE_LIB_PATH, settings.SIGNAL_DATABASE)

# filters and map the IBUS messages against correct action (determinate state)
# Base class. This class handles the raw IBUS messages.
class Filter(object):

	def __init__(self):

		# init events
		# TODO: how should we implement state-machine for buttons?
		self.event = Events()

		# 'map' and 'filter' is x-refereed by its index: 'list[i]'
		# ref: http://kodi.wiki/view/Action_IDs
		self.event_filter = [
			{"src": "IBUS_DEV_BMBT", "data": "right-knob.push", "action": None},
			{"src": "IBUS_DEV_BMBT", "data": "right-knob.hold", "action": None}, # self.action.execute("back")
			{"src": "IBUS_DEV_BMBT", "data": "right-knob.release", "action": None}, # self.action.execute("Select")
			{"src": "IBUS_DEV_BMBT", "data": "right-knob.turn-left", "action": self.event.execute("Left")},
			{"src": "IBUS_DEV_BMBT", "data": "right-knob.turn-right", "action": self.event.execute("Right")},
			{"src": "IBUS_DEV_BMBT", "data": "info.push", "action": None},
		]

		# init Signal-class (convert names to bytes)
		self.signals = Signals(self.event_filter)

	def find_event(self, src, dst, data):

		# find a matching event
		# TODO: what suits best for type on 'src', 'dst', and 'data' (list -or bytearray)?
		# TODO: exclude checksum in 'data'?
		for index, item in enumerate(self.signals.map):

			# proceed if source is correct (empty '_src' means don't evaluate)
			if item.has_key('src') and  item.get('src') != list(src):
				continue

			# proceed if destination is correct (empty '_dst' means don't evaluate)
			if item.has_key('dst') and item.get('dst') != list(dst):
				continue

			# proceed if data is correct (empty '_data' means don't evaluate)
			if item.has_key('data') and item.get('data') != list(data):
				continue

			# We've found a match, stop looking and execute current action.
			execute_action = self.event_filter[index].get('action')

			# execute action
			execute_action()

			# stop searching.
			break


#
# static methods
#


def _str_2_array(str_buf):

	# return a array of integers
	return map(lambda str: int(str, 16), str_buf.split(" "))


# define events and generate calbacks.
class Events(object):

	def __init__(self):
		self.map = list()

		pass

	def execute(self, arg):

		# DEBUG
		#xbmc.log("execute action: %s" % arg, level=xbmc.LOGDEBUG)

		# return a function. ref: http://kodi.wiki/view/Action_IDs
		return lambda: xbmc.executebuiltin("Action(%s)" % arg)
		#return lambda: self.debug_emulate_fcn(arg)

	def debug_emulate_fcn(self, arg):
		print("Execute: %s" % arg)

# TODO: fix better fault-handling for XML-database search..
class Signals(object):

	"""
	Convert signals from name to bytes with help of the XML-database.
	"""

	def __init__(self, signals):

		self.root = None

		# contains the converted bytes
		self.map = list()

		# construct bytearay from XML signal-database
		self.convert_names_to_bytes(signals)


	def convert_names_to_bytes(self, signals):

		tree = ElementTree.parse(SIGNAL_DB_PATH)

		# get root element
		self.root = tree.getroot()

		# iter over constructors -and translate the data references to bytes. - get byte from XML-database.
		for item in signals:

			# dictionary constructor
			ibus_frame = dict()

			if item.has_key('src') and item.get('src'):

				# translate 'source'
				ibus_frame['src'] = self.get_dev(item.get('src'))

			if item.has_key('dst') and item.get('dst'):

				# translate 'destination'
				ibus_frame['dst'] = self.get_dev(item.get('dst'))

			# translate 'data'
			if item.has_key('data') and item.get('data'):

				ibus_frame['data'] = self.get_data(item.get('data'))

			# append also empty items. otherwise we loose the x-referencde.
			self.map.append(ibus_frame)

	def get_dev(self, identifier):

		# find 'src' by id from XML-database
		src = self.root.find("./MESSAGE/DEVICES/byte[@id='%s']" % identifier ).get('val')

		if not len(src):
			print "error - no element found in XML-database"
			return None

		# convert to integer array
		return _str_2_array(src)

	def get_data(self, identifier):

		# get byte from XML-database.
		element = self.root.find("./MESSAGE/DATA/CATEGORY/byte[@id='%s']/.." % identifier )

		if not len(element):
			print "error - no element found in XML-database"
			return None

		# get the refereed byte for 'operation'
		operation = self.root.find("./MESSAGE/DATA/OPERATIONS/byte[@id='%s']" % element.get('ref') ).get('val')

		# get bytes from XML-database
		action = element.find("byte[@id='%s']" % identifier).get('val')

		# merge arrays and return
		return _str_2_array(operation) + _str_2_array(action)

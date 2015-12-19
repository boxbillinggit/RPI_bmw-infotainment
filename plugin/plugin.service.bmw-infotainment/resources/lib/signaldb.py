"""
Create signals from a human-readable reference name using the signal-db.xml
as reference. Returning signal represented in a bytearray.

References:
https://docs.python.org/2/library/xml.etree.elementtree.html
"""

import xml.etree.ElementTree as ElementTree
import os
import settings

import log as log_module
log = log_module.init_logger(__name__)

try:
	import xbmcaddon

except ImportError as err:
	import debug.xbmcaddon as xbmcaddon

__author__ 		= 'Lars'
__addon__		= xbmcaddon.Addon()
__addonpath__	= __addon__.getAddonInfo('path')


# path settings (problem occurs else in XBMC/KODI)
SIGNAL_DB_PATH = os.path.join(__addonpath__, "resources", "data", settings.SIGNAL_DATABASE)


def hexstr_to_int(str_buf):

	# create 'int' array from string
	return map(lambda str: int(str, 16), str_buf.split(" "))


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

"""
Interface for handling signals in a convenient way. By using a human-readable reference-
names when working with signals, instead of handling 'hard-to-read' raw bytearrays.
All signals is now defined in one XML-database instead of spread-out everywhere in the
code. Module returns a signal represented in a bytearray, using the signal-db.xml as reference.

Reference doc:
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


# read XML-database
tree = ElementTree.parse(os.path.join(__addonpath__, settings.SIGNAL_DATABASE))
root = tree.getroot()

HEX_BASE = 16		# hex has base-16


class DBError(Exception):
	"""
	Exception raised if we can't create a signal caused by database references
	"""
	pass


class ArgError(Exception):
	"""
	Exception raised if we can't create a signal caused by not enough arguments
	"""
	pass


def convert_to_bytes(string):
	return map(lambda byte: int(byte, HEX_BASE), string.split(" ")) if string else []


def check_length(obj, ident=""):
	if len(obj) == 1:
		return obj[0]

	raise DBError("{} - {} references(s) found in XML-database for '{}', expecting one item".format(__name__, len(obj), ident))


def get_event(ident):

	"""
	return the event object for further operations in this module.

	defined as <BYTE> within the <ACTION>-tag (formerly <CATEGORY>-tag)
	"""

	obj = root.findall("./MESSAGE/DATA/CATEGORY/byte[@id='{}']/..".format(ident))
	return check_length(obj, ident=ident)


def operation(event):

	"""
	return byte for operation - which is the first byte of the DATA-chunk

	defined within <OPERATIONS>-tag
	"""

	obj = root.findall("./MESSAGE/DATA/OPERATIONS/byte[@id='{}']".format(event.get('ref')))
	return check_length(obj, ident=event.get('ref')).get('val')


def action(event, ident):

	"""
	Return bytes for action - which is the second part of the DATA-chunk

	defined within <ACTION>-tag (formerly <CATEGORY>-tag)
	"""

	# TODO: rename <CATEGORY>-tag to <ACTION> in xml-database
	obj = event.findall("byte[@id='{}']".format(ident))
	return check_length(obj, ident=ident).get('val')


def device(ident):

	"""
	Return bytes for SRC and DST.

	defined within <DEVICES>-tag
	"""

	obj = root.findall("./MESSAGE/DEVICES/byte[@id='{}']".format(ident))
	return convert_to_bytes(check_length(obj, ident=ident).get('val'))


def data(ident):

	"""
	Return bytes for DATA chunk (from operation + action)
	"""

	event = get_event(ident)

	if event is None:
		return None

	return (
		convert_to_bytes(operation(event)) +
		convert_to_bytes(action(event, ident))
	)


def create(src=None, dst=None, event=None):

	"""
	Main function for creating signals from reference-name
	and return signal represented in a 3-tuple (SRC, DST, DATA)
	"""

	# must not be empty, and data must exist. TODO: raise custom error?
	if not (event or (src and dst and event)):
		raise ArgError("Not enough arguments provided.")

	return tuple([
		device(src) if src else None,
		device(dst) if dst else None,
		data(event) if event else None
	])


def create_from_tuple(desc):

	"""
	Create a batch of signals from a list of 3-tuples as input.

	example: [("IBUS_MSG_BMBT_BUTTON", None, "next.push"), ...]
	"""

	signals = []

	for src, dst, event in desc:
		try:
			signals.append(create(src=src, dst=dst, event=event))
		except DBError as error:
			log.error(error)

	return signals

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

# import local modules
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
tree = ElementTree.parse(os.path.join(__addonpath__, settings.SignalDB.PATH))
root = tree.getroot()


class DBError(Exception):
	"""
	Exception raised if we can't create a signal caused by incorrect references
	in database.
	"""
	pass


def uniform(string):

	"""
	When using regular expressions we must use lower cases, etc. Compare what's
	returned from hex(int)
	"""

	return string.replace("0x0", "0x").lower()


def validate(obj, ident=""):
	if len(obj) == 1:
		return obj[0]

	raise DBError("{} - {} references(s) found in XML-database for '{}', expecting one item".format(__name__, len(obj), ident))


def get_event(ident):

	"""
	Return the event object for further operations in this module.

	defined as <BYTE> within the <ACTION>-tag
	"""

	obj = root.findall("./MESSAGE/DATA/ACTION/byte[@id='{}']/..".format(ident))
	return validate(obj, ident=ident)


def operation(event):

	"""
	Return byte for operation - which is the first byte of the DATA-chunk

	defined within <OPERATION>-tag
	"""

	obj = root.findall("./MESSAGE/DATA/OPERATION/byte[@id='{}']".format(event.get('operation')))
	return validate(obj, ident=event.get('operation')).get('val')


def action(event, ident):

	"""
	Return bytes for action - which is the second part of the DATA-chunk

	defined within <ACTION>-tag
	"""

	obj = event.findall("byte[@id='{}']".format(ident))
	return validate(obj, ident=ident).get('val')


def device(ident):

	"""
	Return bytes for SRC and DST.

	defined within <DEVICE>-tag
	"""

	obj = root.findall("./MESSAGE/DEVICE/byte[@id='{}']".format(ident))
	return validate(obj, ident=ident).get('val')


def data(ident):

	"""
	Return bytes for DATA-chunk (from operation + action)
	"""

	event = get_event(ident)

	return None if event is None else (
		operation(event) + " " +
		action(event, ident)
	)


def find(item):

	"""
	Find signal from name.

	Return signal in type string, represented in a 3-tuple (SRC, DST, DATA)
	"""

	src, dst, event = item

	# must not be empty, and data must exist.
	if not (event or (src and dst and event)):
		raise ValueError("Not enough arguments provided")

	return tuple([
		uniform(device(src)) if src else None,
		uniform(device(dst)) if dst else None,
		uniform(data(event))
	])


def create(item):

	"""
	Main function for creating signals from reference-name. Catches exceptions.
	"""

	try:
		return find(item)
	except DBError as error:
		log.error(error)

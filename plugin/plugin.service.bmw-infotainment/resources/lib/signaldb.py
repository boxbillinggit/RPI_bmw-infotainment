"""
Interface for handling signals in a convenient way. By using a human-readable reference-
names when working with signals, instead of handling 'hard-to-read' raw bytearrays.
All signals is now defined in one XML-database instead of spread-out everywhere in the
code. Module returns a signal represented in a hex-string, using the signal-db.xml as
reference.

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

parent = dict((c, p) for p in root.getiterator() for c in p)

DATA = root.find("./MESSAGE/DATA")

NAMESPACE = {
	"signal": "sdb://signal",
	"device": "sdb://device",
	"ref":    "sdb://reference"
}


class DBError(Exception):
	"""
	Exception raised if we can't create a signal caused by incorrect references
	in database.
	"""
	pass


def hex_string(string):

	""" Convert a string (each character) to bytes, represented in a hex-string"""

	return " ".join(map(lambda char: "{:#x}".format(ord(char)), string))


def uniform(string):

	"""
	When using regular expressions we must use lower cases, etc. Compare what's
	returned from hex(int)
	"""

	return string.replace("0x0", "0x").lower()


def validate(obj, ref=""):

	""" Check and validate number of results found from searching xml-db """

	if len(obj) != 1:
		raise DBError("{} - {} references(s) found in XML-database for '{}', expecting one item".format(__name__, len(obj), ref))

	return obj[0]


def get_val(obj):

	""" get value from <byte>-tag """

	val = obj.get('val')

	if not val:
		raise DBError("missing attribute 'val' for tag {}".format(ElementTree.tostring(obj)))

	return val


def get_setting(setting):

	"""	Get communication port settings """

	return validate(root.findall("./COM-SETTINGS/{}".format(setting)), ref=setting).text


def device(attr_id):

	"""	Return bytes for SRC and DST """

	obj = validate(root.findall("./MESSAGE/byte[@device:id='{}']".format(attr_id), NAMESPACE), ref=attr_id)

	return get_val(obj)


def get_byte_from_reference(attr_id):

	""" Get byte with attribute ref:id """

	obj = validate(root.findall("./MESSAGE/DATA//byte[@ref:id='{}']".format(attr_id), NAMESPACE), ref=attr_id)

	return get_val(obj)


def data(attr_id):

	""" traverse upward and replace reference-tag with byte, until end is reached (when parent tag is <DATA>) """

	chunk = []

	data_tag = validate(root.findall("./MESSAGE/DATA//byte[@signal:id='{}']".format(attr_id), NAMESPACE), attr_id)
	chunk.append(get_val(data_tag))
	obj = parent.get(data_tag)

	while not (obj is DATA) or (obj is None):

		chunk.append(get_byte_from_reference(obj.tag))
		obj = parent.get(obj)

	chunk.reverse()

	return " ".join(chunk)


def create(item, **kwargs):

	"""
	Find signal from name.

	Return signal in hex-string, represented in a 3-tuple (SRC, DST, DATA)
	"""

	src, dst, event = item

	# must not be empty, and data must exist.
	if not (event or (src and dst and event)):
		raise ValueError("Not enough arguments provided")

	return tuple([
		uniform(device(src)) if src else None,
		uniform(device(dst)) if dst else None,
		uniform(data(event).format(**kwargs))
	])

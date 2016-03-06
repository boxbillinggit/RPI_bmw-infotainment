"""
This module replaces all <include>-tags in xml-files with a suffix "-source" with
elements from includes.xml since add-on doesn't support includes.xml (as used
when developing skin).
"""
import glob
import os
from xml.dom import minidom
import xml.etree.ElementTree as ET

__author__ 	= 'lars'
PATH 		= os.path.dirname(os.path.abspath(__file__))
SUFFIX 		= "-source"
INCLUDE 	= "includes.xml"
WINDOWS 	= os.path.join(PATH, "*{suffix}.xml".format(suffix=SUFFIX))


includes_tree = ET.parse(os.path.join(PATH, INCLUDE))
includes = includes_tree.getroot()


class XMLLookupError(Exception):

	""" Raised if not found element """
	pass


def new_filename(fname):

	return fname.replace(SUFFIX, "")


def prettify_xml(elem):

	"""	Return a pretty-printed XML string for the Element.	"""

	rough_string = ET.tostring(elem).replace("\t","").replace("\n","")
	return minidom.parseString(rough_string).toprettyxml(indent="\t")


def get_replacement(tag):

	obj = includes.findall("./include[@name='{tag_name}']/*".format(tag_name=tag))

	if obj is None:
		raise XMLLookupError("Could not find include for tag \"{TAG}\"".format(TAG=tag))

	return obj


def replace_includes(tree):

	for tag in tree.getroot().findall('.//include/..'):

		include_tag = tag.find('include')

		tag.remove(include_tag)

		# insert tags first (mus not append)
		[tag.insert(0, _tag) for _tag in get_replacement(include_tag.text)]

		# for asd in get_replacement(include_tag.text):
		# 	print ET.tostring(asd)


def save_xml(fname, _tree):

	try:
		open(new_filename(fname), "wb").write(prettify_xml(_tree.getroot()))

	except OSError as err:
		print err.strerror


if __name__ == "__main__":

	for window in glob.glob(WINDOWS):

		print("Building \"{FILE}\"".format(FILE=new_filename(os.path.basename(window))))

		tree = ET.parse(os.path.join(PATH, window))
		replace_includes(tree)
		save_xml(window, tree)

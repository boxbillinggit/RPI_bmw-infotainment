"""
Creates a zip-archive ready to be installed in KODI
"""
import os
import json
import shutil
import xml.etree.ElementTree as ET

__author__ = 'lars'

PATH 		= os.path.dirname(os.path.abspath(__file__))
ADDON 		= "addon.xml"
PACKAGE 	= "make-package.json"
DESTINATION = "../"


def addon_settings():

	""" read version from addon XML """

	root = ET.parse(ADDON).getroot()

	return root.get("id"), root.get("version")


def create_changelog(addon_ver):

	"""
	Create a changelog with current version-suffix
	"""

	shutil.copy("changelog.txt", "changelog-{VERSION}.txt".format(VERSION=addon_ver))


def package_cfg():

	"""
	Exclude/include files from archive (defined in file with name PACKAGE)
	"""

	cfg = dict()

	if os.path.exists(PACKAGE):

		cfg = json.loads(open(PACKAGE).read())

		# exclude file itself from the archive
		if cfg.get("exclude"):
			cfg.get("exclude").append(PACKAGE)
		else:
			cfg["exclude"] = [PACKAGE]

	return cfg


def create_args(package):

	"""
	Generate arguments defining files to include -or exclude in archive.
	"""

	args = list()

	if package.get("include"):
		[args.append("-i{FILENAME}".format(FILENAME=item)) for item in package.get("include")]

	if package.get("exclude"):
		[args.append("-x{FILENAME}".format(FILENAME=item)) for item in package.get("exclude")]

	return args


def create_archive(addon_id, addon_ver, args):

	filename = "{ID}-{VERSION}.zip".format(ID=addon_id, VERSION=addon_ver)

	try:
		os.system("zip -qr {ARGS} {DST} {FILES}".format(ARGS=" ".join(args), DST=os.path.join(DESTINATION, filename), FILES="*"))

	except OSError as err:
		print err.strerror


if __name__ == "__main__":

	os.chdir(PATH)

	addon_id, addon_ver = addon_settings()

	create_changelog(addon_ver)

	create_archive(addon_id, addon_ver, create_args(package_cfg()))

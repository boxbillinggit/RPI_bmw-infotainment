import hashlib
import xml.etree.ElementTree as ET
import sys, os
from xml.dom import minidom

# path to deploy, trough sftp
SFTP_PATH="public-repository/kodi"
ADDON_DIR="plugin.service.bmw-infotainment"

# this script must be run from folder "deploy"
RELATIVE_PATH="../XBMC plugin"

PATH=os.path.realpath("%s/%s" % (RELATIVE_PATH, ADDON_DIR))


def prettify_xml(elem):
	"""
	Return a pretty-printed XML string for the Element.
	"""

	# replace old tabs and new rows with nothing (else the formatting gets weird)
	rough_string = ET.tostring(elem).replace("\t","").replace("\n","")
	reparsed = minidom.parseString(rough_string)
	return reparsed.toprettyxml(indent="\t")


def generate_master_xml():

	asd = ET.Element("addons")

	# create tree with root element
	out = ET.ElementTree(ET.Element("addons"))

	root = out.getroot()

	# read plugin's addon
	tree = ET.parse(os.path.join(PATH, "addon.xml"))

	addon_xml = tree.getroot()

	# append addon structure
	root.append(addon_xml)

	# write out
	open("addons.xml", "wb" ).write( prettify_xml(root))

	# write out
	#out.write('addons.xml', encoding="UTF-8", xml_declaration=True )

	return addon_xml.get('version'), addon_xml.get('id')


def generate_xml_md5():
	
	# create checksum
	md5 = hashlib.md5( open( "addons.xml", "r" ).read().encode( "utf-8" ) ).hexdigest()

	# write file
	open( "addons.xml.md5" , "wb" ).write(md5)


def move_builds():
	pass


def generate_repository(ver, addon_name):

	archive_name = "%s-%s" % (addon_name, ver)

	try:
		# create folder
		os.mkdir(addon_name)
	except OSError as err:
		print(err.message)

	# copy files
	os.system("cp \"%s/changelog.txt\" \"%s/icon.png\" \"%s/fanart.jpg\" %s" % (PATH, PATH, PATH, addon_name))

	# rename changelog with version-ending
	os.system("mv %s/changelog.txt %s/changelog-%s.txt" % (addon_name, addon_name, ver))

	# finally create the ZIP-archive
	tar_cmd = "tar -cf %s/%s.zip --directory=\"%s\" %s" % (addon_name, archive_name, os.path.realpath(RELATIVE_PATH), ADDON_DIR)
	#print(tar_cmd)

	os.system(tar_cmd)

	# Finally, create sftp batch-comand file for moving files to repository. (dir must exist on remote!)
	sftp_cmd = "put -r %s %s/latest-release\n" % (addon_name, SFTP_PATH) + \
				"put addons.xml %s/xml\n" % (SFTP_PATH) + \
				"put addons.xml.md5 %s/xml\n" % (SFTP_PATH) + \
				"quit\n"

	# create file
	open("sftp.batch", "w" ).write(sftp_cmd)


if __name__ == "__main__":
	plugin_ver, plugin_id = generate_master_xml()
	generate_xml_md5()

	move_builds()

	# prepare files for deploy to repo. (works both on UBUNTU and WIN)
	generate_repository(plugin_ver, plugin_id)

	# if sys.platform == "win32":
	# 	generate_repository_win(plugin_ver, plugin_id)
	# else:
	# 	generate_repository_unix(plugin_ver, plugin_id)

	# TODO: get latest history from GIT and add to changelog ;)
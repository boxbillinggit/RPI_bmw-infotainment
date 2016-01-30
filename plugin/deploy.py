import xml.etree.ElementTree as ET
import os
import hashlib
import glob
from xml.dom import minidom

# mandatory files required in the repository along with the zipped addon
ADDON_COMPONENTS = ("icon.png",	"fanart.jpg", "changelog-*.txt")
MASTER_XML = "addons.xml"

SFTP_ROOT = "public-repository/kodi/release"
SFTP_HOST = "deploy"

files = list()


def prettify_xml(elem):

	"""
	Return a pretty-printed XML string for the Element.
	"""

	rough_string = ET.tostring(elem).replace("\t", "").replace("\n", "")

	return minidom.parseString(rough_string).toprettyxml(indent="\t")


def generate_master_xml(xml_root):

	"""
	Generate the master-xml as a register for all plugins available in the repository.
	Ref: http://kodi.wiki/view/Add-on_repositories
	"""

	xml = prettify_xml(xml_root)

	try:
		open(MASTER_XML, "wb").write(xml)
		open("%s.md5" % MASTER_XML, "wb").write(hashlib.md5(xml).hexdigest())

	except OSError as err:
		print err.strerror

	return MASTER_XML, MASTER_XML + ".md5"


def add_components(plugin_path):

	""" Add rest of the components required in repository """

	for component in ADDON_COMPONENTS:

		try:
			item = glob.glob(os.path.join(plugin_path, component)).pop()
		except IndexError:
			raise IOError("Missing file {FILE}".format(FILE=component))

		files.append((item, os.path.join(SFTP_ROOT, item)))


def deploy(items):

	"""
	Make the actual deployment
	"""

	stdin = list(["END"])

	for src, dst in items:
		stdin.append("put {SOURCE} {DST}".format(SOURCE=src, DST=dst))

	stdin.append("END")

	# deploy files through sftp
	os.system("sftp {HOST} << {STDIN}".format(HOST=SFTP_HOST, STDIN="\n".join(stdin)))


if __name__ == "__main__":

	# create XML-tree with root element
	xml_root = ET.ElementTree(ET.Element("addons")).getroot()

	for xml_file in glob.glob('*/addon.xml'):

		plugin_id = os.path.dirname(xml_file)

		try:
			zip_archive = glob.glob("{PLUGIN}*.zip".format(PLUGIN=plugin_id)).pop()
		except IndexError:
			continue

		files.append((zip_archive, os.path.join(SFTP_ROOT, plugin_id, zip_archive)))

		xml_root.append(ET.parse(xml_file).getroot())

		add_components(plugin_id)

	# add master-xml file
	xml, md5 = generate_master_xml(xml_root)
	files.append((xml, os.path.join(SFTP_ROOT, xml)))
	files.append((md5, os.path.join(SFTP_ROOT, md5)))

	deploy(files)

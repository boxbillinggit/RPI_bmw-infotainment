import xml.etree.ElementTree as ET
from xml.dom import minidom
import hashlib, sys, os

# path to deploy, trough sftp
SFTP_ROOT="public-repository/kodi/release"
SFTP_HOST="deploy@ubuntu"

# set paths according to system
if sys.platform == "win32":
	ROOT_PATH="C:/Users/Lars/Documents/GitHub/bmw-infotainment"
	SFTP_CMD="psftp"
	ZIP_CMD="winrar a -afzip -IBCK -ep1"
else:
	ROOT_PATH=""
	SFTP_CMD="sftp"
	ZIP_CMD="zip -qr"

#UNIX_BUILD_ROOT="~/build/"
#WIN_BUILD_ROOT="C:/Users/Lars/build"

REPOSITORY="tmp-repository"

# Windows configurations: Need to have path on WIN:
# set PATH=C:\Program Files\Putty;%PATH%
# set PATH=C:\Program Files\WinRAR;%PATH%
#ADDON_DIR="plugin.service.bmw-infotainment"

#WIN_SFTP="psftp"	# ref: http://the.earth.li/~sgtatham/putty/0.65/htmldoc/Chapter6.html#psftp

# this script must be run from folder "deploy"
#RELATIVE_PATH="../XBMC plugin"

#PATH=os.path.realpath("%s/%s" % (RELATIVE_PATH, ADDON_DIR))


# TODO
def find_plugins(path):
	return ["plugin/plugin.service.bmw-infotainment"]


def prettify_xml(elem):
	"""
	Return a pretty-printed XML string for the Element.
	"""

	# replace old tabs and new rows with nothing (else the formatting gets weird)
	rough_string = ET.tostring(elem).replace("\t","").replace("\n","")
	reparsed = minidom.parseString(rough_string)
	return reparsed.toprettyxml(indent="\t")


def generate_master_xml(paths):

	data = []

	# create tree with root element
	out = ET.ElementTree(ET.Element("addons"))

	root = out.getroot()

	# iterate over plugin path's
	for path in paths:

		# read plugin's addon
		tree = ET.parse(os.path.join(path, "addon.xml"))

		addon_xml = tree.getroot()

		data.append({"ver": addon_xml.get('version'), "id": addon_xml.get('id')})

		# append addon structure
		root.append(addon_xml)

	# write out
	output = prettify_xml(root)

	# create file
	open("%s/addons.xml" % REPOSITORY, "wb" ).write( output )

	# create checksum
	md5 = hashlib.md5(output).hexdigest()

	# create file
	open( "%s/addons.xml.md5" % REPOSITORY, "wb" ).write(md5)

	# return id -and version
	return data


def move_builds():
	pass


def deploy_repository(relative_path, plugin_ver, plugin_id):

	# Create archive filename
	archive_name = "%s-%s" % (plugin_id, plugin_ver)

	# Create archive
	zip_cmd = "%s %s/%s.zip %s" % (ZIP_CMD, REPOSITORY, archive_name, relative_path)
	os.system(zip_cmd)

	# Linux:
	# 	tar_cmd = "cd \"%s\"\n"% RELATIVE_PATH + \
	# 	"zip -qr ../deploy/%s/%s.zip %s\n" % (addon_name, archive_name, ADDON_DIR)
	#

	# Create sftp batch-comand file for moving files to repository. (dir must exist on remote!)
	sftp_cmd = 	"put %s/addons.xml %s/addons.xml\n" % (REPOSITORY, SFTP_ROOT) + \
				"put %s/addons.xml.md5 %s/addons.xml.md5\n" % (REPOSITORY, SFTP_ROOT) + \
				"put %s/%s.zip %s/%s/%s.zip\n" % (REPOSITORY, archive_name, SFTP_ROOT, plugin_id, archive_name) + \
				"put %s/changelog.txt %s/%s/changelog-%s.txt\n" % (relative_path, SFTP_ROOT, plugin_id, plugin_ver) + \
				"put %s/icon.png %s/%s//icon.png\n" % (relative_path, SFTP_ROOT, plugin_id) + \
				"put %s/fanart.jpg %s/%s/fanart.jpg\n" % (relative_path, SFTP_ROOT, plugin_id) + \
				"quit\n"

	# create file.
	open("%s/sftp.batch" % REPOSITORY, "w" ).write(sftp_cmd)

	# deploy through SFTP
	os.system("%s -b %s/sftp.batch %s" % (SFTP_CMD, REPOSITORY, SFTP_HOST))

if __name__ == "__main__":

	# set working path to root (need to work with relative paths, eg for SFTP)
	os.chdir(ROOT_PATH)

	# create temporary repository folder
	try:
		os.mkdir(REPOSITORY)
	except OSError as err:
		print(err.message)

	# get available plugins
	plugin_paths = find_plugins(ROOT_PATH)

	# generate master xml
	plugin_data = generate_master_xml(plugin_paths)

	# move builds
	#move_builds()

	# prepare files and deploy to to repository.
	for idx, data in enumerate(plugin_data):
		deploy_repository(plugin_paths[idx], data.get("ver"), data.get("id"))

	# TODO: get latest history from GIT and add to changelog ;)

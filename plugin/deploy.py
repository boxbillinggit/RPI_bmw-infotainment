import xml.etree.ElementTree as ET
from xml.dom import minidom
import hashlib, os, glob, json


FNAME_PACKAGE = "package.json"

GIT_CMD = "git log -s --format=medium -n5 --merges"
config = {"xml": "addons.xml"}

# sftp config
SFTP_ROOT="public-repository/kodi/release"
SFTP_HOST="deploy.lan"


def find_plugins():

	return glob.glob('*/addon.xml')


def _prettify_xml(elem):

	"""
	Return a pretty-printed XML string for the Element.
	"""

	# replace old tabs and new rows with nothing (else the formatting gets weird)
	rough_string = ET.tostring(elem).replace("\t","").replace("\n","")
	reparsed = minidom.parseString(rough_string)
	return reparsed.toprettyxml(indent="\t")


def generate_master_xml(plugins, flist):

	"""
	This function generats the master-xml containing all plugins available in the repository.
	Ref: http://kodi.wiki/view/Add-on_repositories
	"""

	plugindata = list()

	# create XML-tree with root element
	out = ET.ElementTree(ET.Element("addons"))
	root = out.getroot()

	for plugin in plugins:

		# read XML-data from addon
		tree = ET.parse(plugin)
		addon_xml = tree.getroot()

		plugindata.append({"path": os.path.dirname(plugin), "ver": addon_xml.get('version'), "id": addon_xml.get('id')})

		if os.path.dirname(plugin) != addon_xml.get('id'):
			print("WARNING: path is not consistent with id defined in addon.xml (plugin id: %s)" % addon_xml.get('id'))

		# append addon structure
		root.append(addon_xml)

	output = _prettify_xml(root)

	fname = config.get("xml")

	try:
		# create files
		open(fname, "wb").write(output)
		flist.append({"src": fname, "dst": "%s/%s" % (SFTP_ROOT, fname)})

		open("%s.md5" % config.get("xml"), "wb").write(hashlib.md5(output).hexdigest())
		flist.append({"src": "%s.md5" % fname, "dst": "%s/%s.md5" % (SFTP_ROOT, fname)})

	except OSError as err:
		print err.strerror

	return plugindata


def create_changelog():

	# TODO: fix this
	#log = subprocess.check_call(GIT_CMD, shell=True)
	#print log
	pass


def _include_files(path):

	args = list()

	# check if we defined some includes, excludes
	fname = os.path.join(path, FNAME_PACKAGE)

	if os.path.exists(fname):

		# exclude file itself in archive
		args.append("-x%s" % fname)

		files = json.loads(open(fname).read())

		if files.get("include"):
			[args.append("-i%s/%s" % (path, f)) for f in files.get("include")]

		if files.get("exclude"):
			[args.append("-x%s/%s" % (path, f)) for f in files.get("exclude")]

	return args


def _get_plugin_files(plugin):

	src_path = plugin.get("path")
	dst_path = os.path.join(SFTP_ROOT, plugin.get("id"))

	return [{"src": "%s/changelog.txt" % src_path, "dst": "%s/changelog-%s.txt" %(dst_path, plugin.get("ver"))},
			{"src": "%s/icon.png" % src_path, "dst": "%s/icon.png" % dst_path},
			{"src": "%s/fanart.jpg" % src_path, "dst": "%s/fanart.jpg" % dst_path}]


def package_plugin(plugins, flist):

	for plugin in plugins:

		# check if we have files to include/exclude in archive
		args = _include_files(plugin.get("path"))

		fname = "%s-%s.zip" % (plugin.get("id"), plugin.get("ver"))

		os.system("zip -qr %s %s %s" % (" ".join(args), fname, plugin.get("path")))

		flist.append({"src": fname, "dst": os.path.join(SFTP_ROOT, plugin.get("id"), fname)})

		# other files needed
		flist.extend(_get_plugin_files(plugin))


def deploy(flist):

	sftp_cmd = list()
	sftp_cmd.append("END")

	for file in flist:
		sftp_cmd.append("put %s %s" % (file.get("src"), file.get("dst")))

	sftp_cmd.append("END")

	# deploy through sftp
	os.system("sftp %s << %s" % (SFTP_HOST, "\n".join(sftp_cmd)))


if __name__ == "__main__":

	# containing all files to be pushed to repository
	flist = list()

	plugins = generate_master_xml(find_plugins(), flist=flist)

	# TODO get latest history from GIT and add to changelog ;)
	create_changelog()

	package_plugin(plugins, flist=flist)

	deploy(flist=flist)

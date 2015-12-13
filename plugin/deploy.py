import xml.etree.ElementTree as ET
from xml.dom import minidom
import os, hashlib, glob, json, subprocess

# ref: http://git-scm.com/docs/git-log
CHANGELOG = "git log -s --format=medium -n1 --merges"
DEPLOY_CFG = "deploy.json"

# mandatory files required in the repository along with the zipped addon
ADDON_COMPONENTS = ["icon.png",	"fanart.jpg"]

# sftp config
SFTP_ROOT="public-repository/kodi/release"
SFTP_HOST="deploy.lan"


def find_plugins():

	return glob.glob('*/addon.xml')


def add_component(src=list(), dstprefix="", flist=list()):

	for component in src:

		if os.path.exists(component):

			flist.append({"src": component, "dst": os.path.join(dstprefix, component) if dstprefix else component})

		else:
			print "WARNING - failed to add component \"%s\". file does not exist!" % component


def generate_changelog(addonpath, ver):

	"""
	create a changelog from git commits (and change suffix on changelog to <version>)
	"""

	heading = "v%s" % ver

	gitlog = subprocess.check_output(CHANGELOG, shell=True)

	# read existing logfile
	log = open(os.path.join(addonpath, "changelog.txt"), "rb").read()

	# create a new logfile with a version suffix
	fname = "changelog-%s.txt" % ver
	open(os.path.join(addonpath, fname), "wb").write("\n".join([heading, gitlog, log]))

	return [os.path.join(addonpath, fname)]


def _prettify_xml(elem):

	"""
	Return a pretty-printed XML string for the Element.
	"""

	# replace old tabs and new rows with nothing (else the formatting gets weird)
	# TODO: use only replace()-function once!
	rough_string = ET.tostring(elem).replace("\t","").replace("\n","")
	reparsed = minidom.parseString(rough_string)

	return reparsed.toprettyxml(indent="\t")


def read_plugin_configuration(plugin):

	# read XML-data from addon
	tree = ET.parse(plugin)
	root = tree.getroot()

	if os.path.dirname(plugin) != root.get("id"):
		print("WARNING - path \"%s\"is not consistent with id \"%s\" (defined in addon.xml)" % (os.path.dirname(plugin), root.get('id')))

	return root


def generate_master_xml(xmlroot):

	"""
	Generate the master-xml as a register for all plugins available in the repository.
	Ref: http://kodi.wiki/view/Add-on_repositories
	"""

	fname = "addons.xml"
	output = _prettify_xml(xmlroot)

	try:
		open(fname, "wb").write(output)
		open("%s.md5" % fname, "wb").write(hashlib.md5(output).hexdigest())

	except OSError as err:
		print err.strerror

	return [fname, "%s.md5" % fname]


def read_deploy_configuration(path):

	"""
	This function looking for a file (defined in DEPLOY_CFG). if no file is found, the plugin is not ready
	to deploy. This configuration-file lists components to include/exclude from the zip-archive.
	"""

	cfg = dict()

	# check if we defined some includes, excludes for deploying
	fname = os.path.join(path, DEPLOY_CFG)

	if os.path.exists(fname):

		cfg = json.loads(open(fname).read())

		# exclude file itself from the archive
		if cfg.get("exclude"):
			cfg.get("exclude").append(DEPLOY_CFG)
		else:
			cfg["exclude"] = [DEPLOY_CFG]

	return cfg


def generate_args(option, path):

	"""
	Generate arguments for the system call zip defining files to include -or
	exclude in archive.
	"""

	args = list()

	if option.get("include"):
		[args.append("-i%s" % fname) for fname in option.get("include")]

	if option.get("exclude"):
		[args.append("-x%s/%s" % (path, fname)) for fname in option.get("exclude")]

	return args


def create_archive(addon, ver, args):

	fname = "%s-%s.zip" % (addon, ver)

	try:
		os.system("zip -qr %s %s %s" % (" ".join(args), fname, addon))

	except OSError as err:
		print err.strerror

	return [fname]


def deploy_files(flist):

	sftp_cmd = list()
	sftp_cmd.append("END")

	for file in flist:
		sftp_cmd.append("put %s %s" % (file.get("src"), file.get("dst")))

	sftp_cmd.append("END")

	# deploy through sftp
	os.system("sftp %s << %s" % (SFTP_HOST, "\n".join(sftp_cmd)))


if __name__ == "__main__":

	# all files pushed to repository
	flist = list()

	# create XML-tree with root element (for master-xml)
	out = ET.ElementTree(ET.Element("addons"))
	xmlroot = out.getroot()

	for plugin in find_plugins():

		pluginpath = os.path.dirname(plugin)

		deploy = read_deploy_configuration(pluginpath)

		if deploy:

			plugin_cfg = read_plugin_configuration(plugin)
			xmlroot.append(plugin_cfg)

			# create archive of addon
			archive = create_archive(pluginpath, plugin_cfg.get("version"), generate_args(deploy, pluginpath))
			add_component(src=archive, dstprefix=os.path.join(SFTP_ROOT, plugin_cfg.get("id")), flist=flist)

			# include other files (icon and fanart)
			add_component(src=map(lambda fname: os.path.join(pluginpath, fname), ADDON_COMPONENTS), dstprefix=SFTP_ROOT, flist=flist)

			# create changelog
			add_component(src=generate_changelog(pluginpath, plugin_cfg.get("version")), dstprefix=SFTP_ROOT, flist=flist)

	# generate the master-xml file
	add_component(src=generate_master_xml(xmlroot), dstprefix=SFTP_ROOT, flist=flist)

	deploy_files(flist)

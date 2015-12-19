import sys, os

# add paths to system path (extending python module search)
rootpath = os.getcwd()

sys.path.extend([
	os.path.join(rootpath, "plugin", "plugin.service.bmw-infotainment"),
	os.path.join(rootpath, "plugin", "script.module.bluetooth"),
	os.path.join(rootpath, "plugin")
])

print("Modules added to sys path!")
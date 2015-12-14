import sys, os

# add modules to paths (because console's root is "/home/lars/git/bmw-infotainment/")
rootpath = os.getcwd()

sys.path.extend([
	os.path.join(rootpath, "plugin", "script.module.bluetooth"),
	os.path.join(rootpath, "plugin")
])

print("Modules added to sys path!")
import sys

# add modules to paths (because console's root is "/home/lars/git/bmw-infotainment/")
sys.path.extend([
	'/home/lars/git/bmw-infotainment/plugin/script.module.bluetooth',
	'/home/lars/git/bmw-infotainment/plugin/'
])

print("Modules added to sys path!")
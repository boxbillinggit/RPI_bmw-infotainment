## Summary

This is the main part addon for controlling KODI/XBMC through IBUS *(via TCP/IP-gateway)*.

- `service.py` - main-part of the addon, launced during start of XBMC/KODI.
- `guicallback.py` - handles callbacks from GUI by launching this script *(buttons, etc)*
- `libguicallback.so` - This is the interface between service -and script. The reason this module exists is 
because there's no other way for the service.py to receive GUI-callbacks. Calling a script launches a 
separate python-interpreter isolated from service.py. Hence the need of a cPython-plugin handling callbacks between the separate python-interpreters.

## Installation - Release

Get latest release [here](http://deploy.one-infiniteloop.com/kodi/release/), see [Wiki](http://git.one-infiniteloop.com/larsa/bmw-infotainment/wikis/home) for installation instructions. Automatic updates is enbled
 and makes it possible to keep the plugin up-to-date after installation!

## Installation - Development

Below you'll find instructions for how to set-up installation during a development processs. This plugin
is developed using PyCharm.

#### 1. Build cPython addon

- Build `guicallback.so` by running build-script in `guicallback/build-<target>.sh`.

#### 2. Install plugin

- Create symlink between XBMC/KODI plugin-path and to your development environment `ln --symbolic ~/git/bmw-infotainment/plugin/plugin.service.bmw-infotainment ~/.kodi/addons/plugin.service.bmw-infotainment`

#### 3. Install Python Debugger

- Install WinPDB (http://winpdb.org/download/)
- Create symlink to `rpdb2.py`-file by executing: `ln --symbolic /usr/lib/python2.7/dist-packages/rpdb2.py ~/git/plugin.service.bmw-infotainment/rpdb2.py`

#### 4. Activate debug-mode in XBMC/KODI *(optional)*
- Activate debugging in `addon.xml` of your current skin *(you can see ID's of the GUI elements)*

#### 5a. Run - in XBMC/KODI
- Start WinPDB *(if activated in `settings.py`)*
- Start XBMC/KODI. 
- Press "Play" in WinPDB for allowing XBMC/KODI to proceed.

#### 5b. Run - Command-line
You can run the plugin from command-line *(outside XBMC/KODI)* during development. This makes parts of the functionality available and easy to evaluate without the need to perform a time-consuming restart of XBMC/KODI each time a change is made.

- Run `__init__`  in PyCharm for fixing the paths for Python-interpreter accordingly to the project.
- Launch service `python service.py` 

## Paths

- logfiles `~/.kodi/temp`
- plugin `~/.kodi/addons`

## References

Python addon development - http://kodi.wiki/view/Add-on_development

API docs for Python - http://mirrors.kodi.tv/docs/python-docs/14.x-helix/

WinPDB - http://kodi.wiki/view/HOW-TO:Debug_python_scripts_with_WinPDB

XBMC/KODI addon.xml - http://kodi.wiki/view/Addon.xml#Overview

Python threads - http://chimera.labs.oreilly.com/books/1230000000393/ch12.html

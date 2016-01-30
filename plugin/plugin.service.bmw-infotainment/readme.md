## Summary

This plugin makes it possible to control KODI/XBMC through LIN-bus *(IBUS)* via TCP/IP-gateway.
`service.py` is the main part in this add-on and runs automatically when KODI starts.

## Installation - Release

Get latest release [here](http://deploy.one-infiniteloop.com/kodi/release/), see [Wiki](http://git.one-infiniteloop.com/larsa/bmw-infotainment/wikis/home) for installation instructions. Automatic updates is enabled
and makes it possible to keep the plugin up-to-date after installation!

## Installation - From source

- run `resources/skins/Default/720p/build-xml.py` to build XML-file for GUI.
- run `make-package.py` to build zip-archive which you can install from XBMC/KODI.

## Installation - During development

Below you'll find instructions for how to set-up installation during a development processs. This plugin
is developed using PyCharm.


#### 1. Install plugin *(with symlinks)*

- Create symlink between XBMC/KODI plugin-path and to your development environment `ln --symbolic ~/git/bmw-infotainment/plugin/plugin.service.bmw-infotainment ~/.kodi/addons/plugin.service.bmw-infotainment`

#### 2. Install Python Debugger

- Install WinPDB (http://winpdb.org/download/)
- Create symlink to `rpdb2.py`-file by executing: `ln --symbolic /usr/lib/python2.7/dist-packages/rpdb2.py ~/git/plugin.service.bmw-infotainment/rpdb2.py`

#### 3. Activate debug-mode in XBMC/KODI *(optional)*
- Activate debugging in `addon.xml` of your current skin *(you can see ID's of the GUI elements)*

#### 4a. Run - in XBMC/KODI
- Start WinPDB *(if activated in `settings.py`)*
- Start XBMC/KODI. 
- Press "Play" in WinPDB for allowing XBMC/KODI to proceed.

#### 4b. Run - Command-line
You can run the plugin from command-line *(outside XBMC/KODI)* during development. This makes parts of the functionality available and easy to evaluate without the need to perform a time-consuming restart of XBMC/KODI each time a change is made.

- import `__init__.py`  in PyCharm for fixing the paths for Python-interpreter accordingly to the project.
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

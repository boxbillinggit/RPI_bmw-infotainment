## Overview

This is the main addon for controlling KODI/XBMC through IBUS *(via TCP/IP-gateway)*.

- `service.py` - main-part of the addon, launced during start of XBMC/KODI
- `default-handler.py` - handles callbacks from GUI by launching this script *(buttons, etc)*
- `bmwaddon.so` - This is the glue between service -and script. The reason this module exists is 
because there's no other way for the service.py to receive GUI-callbacks. Calling a script launches a 
separate python-interpreter isolated from service.py.

## Installation - Release

See [Wiki](http://git.one-infiniteloop.com/larsa/bmw-infotainment/wikis/home) for 
installation instructions. Get latest release [here](http://deploy.one-infiniteloop.com/kodi/release/), automatic updates is enbled
for receiving latest release after installation! 

## Installation - Development

Below you'll find instructions for how to set-up installation during a development processs.This plugin
is developed using PyCharm.

#### 1. Build cPython addon

- Build `plugin.module` and place artifact *(bmwaddon.so)* in `plugin.service.bmw-infotainment/` path.

#### 2. Install Python Debugger

- Get WinPDB and install http://winpdb.org/download/ 
- Create symlink to `rpdb2.py`-file by executing: `ln --symbolic <path-to-debugger>/rpdb2.py <path-to-plugin>/rpdb2.py`

#### 3. Activate debug-mode in XBMC/KODI *(optional)*
- Activate debugging in `addon.xml` of your current skin *(you can see ID's of the GUI elements)*

#### 4a. Run - in XBMC/KODI
- Create symlink between source and plugin-directory in KODI `ln --symbolic <kodi-pluin-path>/ <path-to-plugin>/`
- Start WinPDB *(if activated in `settings.py`)*
- Start XBMC/KODI. 
- Press "Play" in WinPDB for allowing XBMC/KODI to proceed.

#### 4b. Run - Command-line

- Run `__init__`  in PyCharm for fixing the paths for Python-interpreter accordingly to the project.
- Launch service `python service.py` 

## References
Python addon development - http://kodi.wiki/view/Add-on_development

API docs for Python - http://mirrors.kodi.tv/docs/python-docs/14.x-helix/

WinPDB - http://kodi.wiki/view/HOW-TO:Debug_python_scripts_with_WinPDB

XBMC/KODI addon.xml - http://kodi.wiki/view/Addon.xml#Overview

Python threads - http://chimera.labs.oreilly.com/books/1230000000393/ch12.html
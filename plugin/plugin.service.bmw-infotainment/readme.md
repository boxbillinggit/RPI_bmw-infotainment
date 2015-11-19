# Description

This is the main addon for controlling KODI/XBMC through IBUS *(via TCP/IP-gateway)*.

# Overview

`service.py` - Service-part of plugin, also the main-part of the addon *(launced from XBMC/KODI during start)* 

`default-handler.py` - Script-part of plugin, handles callbacks from GUI *(buttons, etc)*

`bmwaddon.so` - This is the glue between service -and script. The reason this module exists is 
because there's no other way for the service.py to receive GUI-callbacks. Calling a script launches a 
separate python-interpreter isolated from service.py.


## 1a. Installation - Release

See [Wiki](http://git.one-infiniteloop.com/larsa/bmw-infotainment/wikis/home) for 
installation instructions. Get latest release [here](http://deploy.one-infiniteloop.com/kodi/release/). Automatic updates is enbled
for receiving latest release after installation! 

## 1b. Installation - Development

Below you'll find instructions for how to set-up installation during a development processs.This plugin
is developed using PyCharm.

#### 1. Preparation - Build cPython addon

- Build `plugin.module` and place artifact *(bmwaddon.so)* in `plugin.service.bmw-infotainment/` path.
- Create symlink between source and plugin-directory in KODI `ln --symbolic <kodi-pluin-path>/ <path-to-plugin>/`

#### 2. Preparation - Install Python Debugger

- Get WinPDB and install http://winpdb.org/download/ 
- Create symlink to `rpdb2.py`-file by executing: `ln --symbolic <path-to-debugger>/rpdb2.py <path-to-plugin>/rpdb2.py`

#### 3. Preparation - Activate debug-mode *(optional)*
- Activate debugging in `addon.xml` of your current skin *(you can see ID's of the GUI elements)*


#### 4a. Run - Command-line

1. Run `__init__`  in PyCharm for fixing the paths for Python-interpreter accordingly to the project.
2. Launch service `python service.py` 

#### 4b. Run - Through XBMC/KODI

1. Start WinPDB *(if activated in `settings.py`)*
2. Start XBMC/KODI. 
3. Press "Play" in WinPDB for allowing XBMC/KODI to proceed.

# References
Python addon development - http://kodi.wiki/view/Add-on_development

Python threads - http://chimera.labs.oreilly.com/books/1230000000393/ch12.html

API docs for Python - http://mirrors.kodi.tv/docs/python-docs/14.x-helix/

XBMC/KODI addon.xml - http://kodi.wiki/view/Addon.xml#Overview
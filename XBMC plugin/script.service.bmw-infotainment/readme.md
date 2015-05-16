## Contribute!

To continue developing client, best practice to keep source within git repo is to create a symbolic link
in kodi/addons/

run cmd.exe (as administrator)

execute: (mklink --help)
> mklink /D "C:\Program Files\Kodi\addons\script.service.bmw-infotainment" "C:\Users\Lars\Documents\GitHub\bmw-infotainment\XBMC plugin\script.service.bmw-infotainment"


# KODI API docs



# OpenBM-gateway
Launch gateway on Raspberry Pi:
> ./gateway -d /dev/ttyUSB0 -i 0.0.0.0

if somethong goes wrong on OpenBM-daemon, kill proces by:
get process ID from "ps aux | grep ./gateway"
kill process "kill [Process ID]"


## Requirements / recommendations
* install PyCharm (Python development environment)
* install WinPDB (debugger) http://winpdb.org/download/

> mklink "C:\Users\Lars\Documents\GitHub\bmw-infotainment\XBMC plugin\script.service.bmw-infotainment\rpdb2.py" "C:\Program Files\Python\Lib\site-packages\rpdb2.py"

## references
Python addon development: http://kodi.wiki/view/Add-on_development
aGood reference about threads:  http://chimera.labs.oreilly.com/books/1230000000393/ch12.html
API docs for Python:  http://mirrors.kodi.tv/docs/python-docs/14.x-helix/
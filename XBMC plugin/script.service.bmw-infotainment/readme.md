## Contribute!

To continue developing client, best practice to keep source within git repo is to create a symbolic link
in kodi/addons/

run cmd.exe (as administrator)

execute: (mklink --help)
> mklink /D "C:\Program Files\Kodi\addons\script.service.bmw-infotainment" "C:\Users\Lars\Documents\GitHub\bmw-infotainment\XBMC plugin\script.service.bmw-infotainment"


# KODI API docs
*for Python*
 http://mirrors.kodi.tv/docs/python-docs/14.x-helix/


# OpenBM-gateway
Launch gateway on Raspberry Pi:
> ./gateway -d /dev/ttyUSB0 -i 0.0.0.0
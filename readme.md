# BMW infotainment

For detailed description -and further instructions, please see [Wiki](http://git.one-infiniteloop.com/larsa/bmw-infotainment/wikis/home).

### Overview

- `Deploy/` Script for deploying complete package to public repository after a build (continuous-integration)
- `gateway/` Sourcecode for LIN-bus TCP/IP gateway
- `plugin/` Main XBMC/KODI-plugin
 - `plugin.module/` cPython library for supporting *plugin.service.bmw-infotainment*-plugin
 - `plugin.service.bmw-infotainment` Main script for controlling XBMC/KODI through LIN-bus
 - `script.module.bluetooth` Handles the bluetooth-interface through DBus

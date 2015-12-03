## Overview

- `deploy/` Script for deploying complete package to public repository after a build (continuous-integration)
- `gateway/` Sourcecode for LIN-bus TCP/IP gateway
- `plugin/` Main XBMC/KODI-plugin
 - `plugin.module/` cPython library for supporting *plugin.service.bmw-infotainment*-plugin
 - `plugin.service.bmw-infotainment/` Main script for controlling XBMC/KODI through LIN-bus
 - `script.module.bluetooth/` Handles the bluetooth-interface through DBus
- `.gitlab-ci.yml` Configuration file for GitLab CI (continuous integration)
- `__init__.py ` Init script fixing paths when using Python-interpreter in PyCharm (run `__init__`)

## References
 For detailed description -and further instructions, please see [Wiki](http://git.one-infiniteloop.com/larsa/bmw-infotainment/wikis/home).
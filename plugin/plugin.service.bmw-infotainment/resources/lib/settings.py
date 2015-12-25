"""
Contain all settings for the script
"""

__author__ = 'Lars'
import os
import logging

#
# WinPDB (windows python debugger)
#

# if we're attempting to use WinPDB as debugger (we need to open the debugger before XBMC/KODI proceeds..)
DEBUGGER_ON = False
DEBUGGER_TIMEOUT = 30

#
# log settings
#

LOG_TO_CONSOLE = True
LOG_TO_FILE = True
LOG_FILENAME_UNIQUE = False

LOGLEVEL_CONSOLE = logging.INFO
LOGLEVEL_FILE = logging.DEBUG

#
# TCP/IP connection config
#

# limit number of max connections (if something fatal goes wrong).
MAX_RECONNECT = 5

# module IBUSHandler
SIGNAL_DATABASE = os.path.join("resources", "data", "signal-db", "SignalDatabase.xml")

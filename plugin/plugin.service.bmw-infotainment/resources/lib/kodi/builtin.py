"""
Events against KODI using builtin API.

Reference:
http://kodi.wiki/view/List_of_Built_In_Functions
http://kodi.wiki/view/keymap#Actions
http://kodi.wiki/view/Action_IDs
"""
import time
from __init__ import __xbmc__

__author__ = 'lars'

SCROLL_SPEED = 0.01


def shutdown():

	"""	system shutdown has been requested """

	# __xbmc__.shutdown()  # we don't want abrupt shutdown during testing ;)
	__xbmc__.executebuiltin("Quit")


def action(event):

	""" Factory method for creating callback."""

	return lambda: _action(event)


def scroll(direction):

	"""
	Factory method for creating callback for e'scrolling (supports different
	scroll-speeds
	"""

	return lambda *args: _action(direction, *args)


def _action(event, *args):

	"""
	Execute an action in KODI (could be repeatedly).
	"""

	repeat = int(args[0]) if args else 1

	for n in range(repeat):

		if n > 0:
			time.sleep(SCROLL_SPEED)

		__xbmc__.executebuiltin("Action({event})".format(event=event))

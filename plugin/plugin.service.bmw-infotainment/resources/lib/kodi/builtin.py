"""
Events against KODI using builtin API.

Reference:
http://kodi.wiki/view/List_of_Built_In_Functions
http://kodi.wiki/view/keymap#Actions
http://kodi.wiki/view/Action_IDs
http://mirrors.kodi.tv/docs/python-docs/14.x-helix/
"""
import time
from __init__ import __xbmc__, __player__

__author__ = 'lars'

SCROLL_SPEED = 0.01


def shutdown():

	"""	system shutdown has been requested """

	__xbmc__.shutdown()


def action(event):

	""" Factory method for creating callback."""

	return lambda: _action(event)


def scroll(direction):

	"""	Factory method for creating callback for e'scrolling (supports different
	scroll-speeds """

	return lambda *args: _action(direction, *args)


def _action(event, *args):

	"""	Execute an action in KODI (could be repeatedly). """

	repeat = int(args[0]) if args else 1

	for n in range(repeat):

		if n > 0:
			time.sleep(SCROLL_SPEED)

		__xbmc__.executebuiltin("Action({event})".format(event=event))


def pause():

	""" Not using stop(), since we loosing current playlist then (can't resume).. """

	if __xbmc__.getCondVisibility("Player.Playing"):
		__player__.pause()


def play():

	""" pause() is toggling: play-pause-play.. """

	if __xbmc__.getCondVisibility("Player.Paused"):
		__player__.pause()


def media_ctrl(command):

	__xbmc__.executebuiltin("PlayerControl({COMMAND})".format(COMMAND=command))

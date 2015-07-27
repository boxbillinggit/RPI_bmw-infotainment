__author__ = 'Lars'

import time
from threading import Thread

try:
	# Python dev docs: http://mirrors.kodi.tv/docs/python-docs/14.x-helix/
	import xbmc, xbmcplugin, xbmcgui, xbmcaddon

	__addon__		= xbmcaddon.Addon()
	__addonid__		= __addon__.getAddonInfo('id')

except ImportError as err:
	from debug import XBMC
	xbmc = XBMC()

	__addonid__ 	= "script.ibus.bmw"

	print "WARNING: Failed to import XBMC/KODI modules - using 'XBMCdebug'-module instead."

# define timing in seconds [s] for state "hold"
STATE_HOLD_TIME = 1
STATE_HOLD_TIME_INIT = 2
STATE_HOLD_TIME_ABORT = 5


# Base class. Constructor for all buttons -and its states
class Button(object):

	def __init__(self):
		pass

	def create(self, button, states):

		# create button, and map against states
		setattr(self, button, States(states))

	# called when a button isn't found in namespace
	# TODO: better handling. (if calling 'not_existing_button.hold()'
	# def __getattr__(self, namespace):
	#
	# 	xbmc.log("%s: %s - No button found for '%s'" % (__addonid__, self.__class__.__name__, namespace), xbmc.LOGDEBUG)


# Construction class. Create states for each button
class States(object):

	"""
	States generated for buttons:
		* push
		* hold
		* release
	"""

	def __init__(self, action):

		# init variables
		self.action = action
		self.timestamp = time.time()

		# init with the state 'release'
		self.state = "release"
		self.previous_state = None

	# check if we're holding button pressed long enough...
	def _still_holding(self):

		t = time.time() - self.timestamp

		return t < STATE_HOLD_TIME_ABORT and self.state != "release"

	# periodic execution during state 'hold'
	def _check_state_hold(self):

		xbmc.log("%s: %s - init the while loop for state 'hold'" % (__addonid__, self.__class__.__name__), xbmc.LOGDEBUG)

		# loop until we're in state 'release' or max time has occurred.
		while self._still_holding():

			# if we're have a message on the bus, we don't want to interfere with this event
			if self.previous_state == "hold":
				time.sleep(STATE_HOLD_TIME)
			else:
				time.sleep(STATE_HOLD_TIME_INIT)

			# execute action
			self.hold()


		xbmc.log("%s: %s - exits the while loop for state 'hold'" % (__addonid__, self.__class__.__name__), xbmc.LOGDEBUG)

	# start the timer when holding button (to evaluate if holding)
	def _start_timer(self):

		# create and start a timer thread.
		t = Thread(name='ButtonStateHold', target=self._check_state_hold)
		t.daemon = True
		t.start()

		xbmc.log("%s: %s - start loop in thread for 'hold'" % (__addonid__, self.__class__.__name__), xbmc.LOGDEBUG)

	# action for state 'push'.
	def push(self):

		self.state = "push"
		self.timestamp = time.time()

		xbmc.log("%s: %s - triggered state '%s'" % (__addonid__, self.__class__.__name__, self.state), xbmc.LOGDEBUG)

		# check that action for state 'hold' is not empty, else don't bother start timer.
		# must be triggered only if previous state was 'release' (none is the init previous state)
		if self.action.get('hold') and self.previous_state == ("release" or None):

			self._start_timer()

		# execute action for 'push'...
		action = self.action.get('push')

		# ...if it is a function
		if hasattr(action, '__call__'):
			action()
		else:
			xbmc.log("%s: %s - state '%s' has no action" % (__addonid__, self.__class__.__name__, self.state), xbmc.LOGDEBUG)

		self.previous_state = self.state


	# action for state 'hold'. (some buttons has a message on the bus for this state already)
	def hold(self):

		self.state = "hold"

		xbmc.log("%s: %s - triggered state '%s'" % (__addonid__, self.__class__.__name__, self.state), xbmc.LOGDEBUG)

		# execute action for 'hold'...
		action = self.action.get('hold')

		# ...if it is a function
		if hasattr(action, '__call__'):
			action()
		else:
			xbmc.log("%s: %s - state '%s' has no action" % (__addonid__, self.__class__.__name__, self.state), xbmc.LOGDEBUG)

		self.previous_state = self.state

	# action for state 'release'
	def release(self):

		# update current state
		self.state = "release"

		xbmc.log("%s: %s - triggered state '%s'" % (__addonid__, self.__class__.__name__, self.state), xbmc.LOGDEBUG)

		# If previous state was 'hold' or 'release' we won't execute action 'release'.
		if self.previous_state == ("hold" or "release"):
			return

		# execute action for 'release'...
		action = self.action.get("release")

		# ...if it is a function
		if hasattr(action, '__call__'):
			action()
		else:
			xbmc.log("%s: %s - state '%s' has no action" % (__addonid__, self.__class__.__name__, self.state), xbmc.LOGDEBUG)

		self.previous_state = self.state

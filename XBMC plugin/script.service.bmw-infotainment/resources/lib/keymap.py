__author__ = 'Lars'


import time
from threading import Thread


try:
	# Python dev docs: http://mirrors.kodi.tv/docs/python-docs/14.x-helix/
	import xbmc, xbmcplugin, xbmcgui, xbmcaddon

except ImportError as err:
	print "WARNING: Failed to import XBMC/KODI modules."

# XBMC controls:
# 	command for control: xbmc.executebuiltin("Action(select)")
#
# 	reference: (hieraecally)
#	http://kodi.wiki/view/keymap
# 	http://kodi.wiki/view/List_of_Built_In_Functions
#	http://mirrors.kodi.tv/docs/python-docs/14.x-helix/xbmc.html#-executebuiltin


# keymaps. maps IBUS messages to controls in XBMC/KODI

# direct mapping for actions.
class Actions(object):

	def __init__(self):
		pass

	# this is last method in method search, if no method exist here is where we ends up.
	# for actions (not states). Methods not included in state_map above, if no attribute exist we'll landing here

	# for not defined states in class 'States' is actions (direct action mappings)
	def __getattr__(self, namespace):

		# error message
		def method_err():
			print "no action defined named %s" % namespace

		# execute action for 'push'...
		try:
			action = self.action[namespace]

		except KeyError:
			return method_err

		# ...if it is a function
		if hasattr(action, '__call__'):
			return action
		else:
			# ...or execute default action with the argument
			# TODO: bad solution, must return a method with an argument though...
			return lambda: self.default_method(action)


# Construction class. Create states for each button (three states pre-defined, see 'state_map')
class States(Actions):

	# define timing in seconds [s] for state "hold"
	HOLD_TIME = 1
	HOLD_TIME_ABORT = 5

	# states covered in this class. States not defined here will be categorisized as an action instead
	# and execute a direct action instead.
	state_map = {
		0 : "push",
		1 : "hold",
		2 : "release"
	}

	def __init__(self, default_method, action):

		# init variables
		self.action = action
		self.default_method = default_method
		self.timestamp = time.time()

		# init state 'release'
		self.state = self.state_map[2]

		# Init Base class
		Actions.__init__(self)

	# periodic execution during state 'hold'
	def check_state_hold(self):

		# check if we're holding button pressed long enough...
		def still_holding():

			t = time.time() - self.timestamp

			return t < self.HOLD_TIME_ABORT and self.state != "release"

		print "DEBUG: init the while loop for 'hold'"

		# loop until we're in state 'release' or max time has occured.
		while still_holding():

			# execute action, restart timer.
			self.hold()

			# sleep for a while
			time.sleep(self.HOLD_TIME)

		print "DEBUG: exit thread 'ButtonStateHold'"

	# start the timer when holding button (to evaluate if holding)
	def start_timer(self):

		# create and start a timer thread.
		t = Thread(name='ButtonStateHold', target=self.check_state_hold)
		t.daemon = True
		t.start()

		print "start loop in thread for 'hold'"

	# action for state 'push'.
	def push(self):

		self.timestamp = time.time()

		print "state push"

		# Check if we're having an action for hold, else don't bother start timer.
		#if hasattr(self.action[ self.state_map[1] ], '__call__'):

		# check that action for state 'hold' is not empty, else don't bother start timer.
		# TODO: must not be triggered again by push/hold state (must be triggered only if previous state was 'release'?)
		if self.action[self.state_map[1]] and self.state == self.state_map[2]:

			self.start_timer()

		# update current state
		self.state = self.state_map[0]

		# execute action for 'push'...
		action = self.action[self.state]

		# ...if it is a function
		if hasattr(action, '__call__'):
			action()
		else:
			# ...or execute default action with the argument
			self.default_method(action)

	# action for state 'hold'. (some buttons has a message on the bus for this state already)
	def hold(self):
		self.state = self.state_map[1]

		print "state hold"

		# execute action for 'hold'...
		action = self.action[self.state]

		# ...if it is a function
		if hasattr(action, '__call__'):
			#print "execute action for hold"
			action()
		else:
			# ...or execute default action with the argument
			self.default_method(action)

	# action for state 'release'
	def release(self):

		print "state release"

		# If previous state was 'hold' we won't execute action 'release'.
		if self.state != self.state_map[1]:

			# execute action for 'release'...
			action = self.action["release"]

			# ...if it is a function
			if hasattr(action, '__call__'):
				action()
			else:
				# ...or execute default action with the argument
				self.default_method(action)

		# update current state
		# TODO get state from this function name instead?
		self.state = self.state_map[2]

class SignalDatabase(object):
	# TODO: read - XML signal database and generate listeners

	def __init__(self):

		self.listeners = {}



# filters and map the IBUS messages against correct action (determinate state)
# Base class. This class handles the raw IBUS messages.
class filter(object):

	SIGNAL_DATABASE = 'signal-database.xml'

	def __init__(self):

		# creates the messages and maps the actions.
		self.map = SignalDatabase(self.SIGNAL_DATABASE)

	def filer_msg(self, src, dst, data):

		# find a match TODO: exclude checksum (last byte in data)?
		for _src, _dst, _data in self.map:

			# proceed if source is correct (empty '_src' means don't evaluate)
			if _src and _src != src:
				continue

			# proceed if destination is correct (empty '_dst' means don't evaluate)
			if _dst and _dst != dst:
				continue

			# proceed if data is correct (empty '_data' means don't evaluate)
			if _data and _data != data:
				continue

			# We've found a match, stop looking and execute current action.
			# TODO: execute action.
			break


# define all buttons.
class KeyMap(object):

	def __init__(self):

		# http://bytebaker.com/2008/11/03/switch-case-statement-in-python/
		# the actual map. execute local function.
		# keyword : local function in "state()"
		# TODO: get data from 'self.map'
		setattr(self, "right_button", States(self.execute, {

				# "state" : "XBMC/KODI action"
				"push": self.no_action,
				"hold": "back",
				"release": "Select",

				# direct actions (not states)
				# "action" : "XBMC/KODI action"
				"rotate_left": "Left",
				"rotate_right": "Right",
		}))

	# Execute the built-in control action for XBMC/KODI
	# ref: http://kodi.wiki/view/Action_IDs
	def execute(self, arg):

		xbmc.log("execute action: %s" % arg, level=xbmc.LOGDEBUG)
		return xbmc.executebuiltin("Action(%s)" % arg)

	# no action
	def no_action(self):
		print "no action"
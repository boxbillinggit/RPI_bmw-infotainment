__author__ = 'Lars'


import time

# Python dev docs: http://mirrors.kodi.tv/docs/python-docs/14.x-helix/
import xbmc, xbmcplugin, xbmcgui, xbmcaddon


# XBMC controls:
# 	command for control: xbmc.executebuiltin("Action(select)")
#
# 	reference: (hieraecally)
#	http://kodi.wiki/view/keymap
# 	http://kodi.wiki/view/List_of_Built_In_Functions
#	http://mirrors.kodi.tv/docs/python-docs/14.x-helix/xbmc.html#-executebuiltin


# keymaps. maps IBUS messages to controls in XBMC/KODI


# handlers for each button
class ButtonHandler:

	# define time for state "hold"
	HOLD_TIME = 1

	states = {
		0 : "push",
		1 : "hold",
		2 : "release-short",
		3 : "release-long"
	}

	def __init__(self):

		self.timestamp = 0
		self.state = None


	def state(self):
		print "TODO"

	def push(self):
		self.state = self.states[0]
		self.timestamp = time.time()

	def hold(self):
		self.state = self.states[1]

	def release(self):

		if (time.time() - self.timestamp) < self.HOLD_TIME:
			self.state = self.states[2]
		else:
			self.state = self.states[3]

		# return the state
		return self.state


# filters the IBUS messages
class filter:

	def __init__(self):

		# empty entity means it doesn't matter.
		self.map = {
			"right-button.push" : 			{"src:": "", "dst": "", "data": ""},
			"right-button.hold" : 			{"src:": "", "dst": "", "data": ""},
			"right-button.release" :		{"src:": "", "dst": "", "data": ""},
			"right-button.rotate-left" 	: 	{"src:": "", "dst": "", "data": ""},
			"right-button.rotate-right" : 	{"src:": "", "dst": "", "data": ""},
		}


# map the IBUS messages against correct action (determinate state)
class Map:

	def __init__(self):

# http://bytebaker.com/2008/11/03/switch-case-statement-in-python/

		# the actual map. execute local function.
		# keyword : local function in "state()"
		self.map = {
			"right-button.push" : "right_button_push",
			"right-button.hold" : "right_button_hold",
			"right-button.release" : "right_button_release",
			"right-button.rotate-left" : "right_button_rotate_left",
			"right-button.rotate-right" : "right_button_rotate_right",
		}


	# Execute the built-in control action
	# ref: http://kodi.wiki/view/Action_IDs
	def action(self, arg):
		xbmc.executebuiltin("Action(%s)" % arg)


	# Determinate action dependent of state
	def state(self, arg):

		def right_button_push():
			print "hej"
			# start timer (or use "right_button_hold"?)

		def right_button_hold():
			print "hello"

		def right_button_release():

			# long push triggers "Back"
			if "long-push" in self.state_of_button:
				self.action("Select")

			# short push triggers "Enter/Select"
			elif "short-push" in self.state_of_button:
				self.action("back")

			else:
				xbmc.log("unknown state for button.  TODO: print out class/module here..")

		def right_button_rotate_left():
			self.action("Left")

		def right_button_rotate_right():
			self.action("Right")
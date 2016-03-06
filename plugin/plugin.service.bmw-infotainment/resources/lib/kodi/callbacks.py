"""
Module for callbacks between GUI and Application
"""
__author__ = 'lars'

# all callbacks
CONNECT 		= "onConnect"
DISCONNECT 		= "onDisconnect"
UPDATE_STATUS 	= "onConnectionStatus"
UPDATE_STATS 	= "onBusActivity"


def default_callback(*args, **kwargs):

	""" default handler when callbacks is unbound (instance is deleted) """

	pass


class Application(object):

	""" Current interface for callbacks in Application """

	Callbacks = {}
	Storage = {}

	@classmethod
	def event(cls, callback, *args, **kwargs):

		method = cls.Callbacks.get(callback, default_callback)
		cls.Storage.update({callback: (args, kwargs)})

		method(*args, **kwargs)


class GUI(object):

	"""	Current interface for callbacks in GUI """

	Callbacks = {}
	Storage = {}

	@classmethod
	def event(cls, callback, *args, **kwargs):

		method = cls.Callbacks.get(callback, default_callback)
		cls.Storage.update({callback: (args, kwargs)})

		method(*args, **kwargs)


def last_BusActivity():

	args, kwargs = GUI.Storage.get("onBusActivity")
	return args[0]


def last_ConnectionStatus():

	args, kwargs = GUI.Storage.get("onConnectionStatus")
	return args[0]

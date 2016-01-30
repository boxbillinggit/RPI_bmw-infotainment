from callbacks import GUI, Application, last_BusActivity, last_ConnectionStatus, CONNECT, DISCONNECT
from __init__ import __addon__, __addonpath__, __xbmcgui__

window_stack = {}


def open_window(Window):

	"""
	Show add-on overview window. This shall be called from Main-thread since
	this method is blocking.
	"""

	window = Window.new()
	window_stack.update({Window.__name__: window})
	window.doModal()
	window.unbind_callbacks()
	window_stack.pop(Window.__name__, None)
	del window


def close_all_windows():

	""" close all windows in stack """

	for window in window_stack.values():
		window.close()

	window_stack.clear()


class AddonOverview(__xbmcgui__.WindowXML):

	"""
	GUI for add-on default overview
	"""

	BUS_ACTIVITY = 101
	CONN_STATUS  = 102

	@classmethod
	def new(cls):

		""" Factory for creating new window """

		return cls("window-info.xml", __addonpath__)

	@staticmethod
	def unbind_callbacks():

		""" Unbind events before deleting object """

		GUI.Callbacks.clear()

	def __init__(self, *args, **kwargs):
		super(AddonOverview, self).__init__()
		self._bind_callbacks()

		self.ui_callbacks = {
			94: __addon__.openSettings,
			200: Application.Callbacks.get(CONNECT),
			201: Application.Callbacks.get(DISCONNECT)
		}

	def _bind_callbacks(self):

		""" Set callbacks, triggered from Application """

		GUI.Callbacks.update(onBusActivity=self.on_bus_activity)
		GUI.Callbacks.update(onConnectionStatus=self.on_connection_status)


	def on_bus_activity(self, percent):

		""" callback from TCP-service """

		label = self.getControl(self.BUS_ACTIVITY)
		label.setLabel("Bus-activity: {percent:.2%}".format(percent=percent))

	def on_connection_status(self, status):

		""" callback from TCP-service """

		label = self.getControl(self.CONN_STATUS)
		label.setLabel("Status: {status}".format(status=status.capitalize()))

	def onInit(self):

		""" Initialize data-fields """

		self.on_bus_activity(last_BusActivity())
		self.on_connection_status(last_ConnectionStatus())

	def onClick(self, ctrl_id):

		"""	Callback from GUI, execute method """

		method = self.ui_callbacks.get(ctrl_id)

		if method:
			method()

"""
This module generate the dynamic content and loads the XML-files.
"""

from bluetooth_core import BluetoothHandler

try:
	import xbmc, xbmcplugin, xbmcgui, xbmcaddon

except ImportError as err:
	#log.warning("%s - using 'debug.XBMC*'-modules instead" % err.message)
	import debug.xbmc as xbmc
	import debug.xbmcgui as xbmcgui
	import debug.xbmcaddon as xbmcaddon

__author__ = 'lars'
__addon__		= xbmcaddon.Addon()
__addonname__	= __addon__.getAddonInfo('name')
__addonpath__	= __addon__.getAddonInfo('path')


ID_DEVICE_LIST = 100

DEVICE_ICON = {
	"phone": "phone-64px.png",
	"computer": "",
	"unknown": "",
}

def init_window(name):

	# create window instance
	window = GUI(name, __addonpath__)

	# Wait until window is closed
	window.doModal()
	del window


class GUI(xbmcgui.WindowXML):

	def __init__(self, *args, **kwargs):

		# init bluetooth handler (set callback handler)
		# TODO: not best solution? (use class inheritance?)
		self.bluetooth = BluetoothHandler(self.device_found)
		#self.bluetooth = BluetoothHandler()

		pass
		# http://kodi.wiki/view/HOW-TO:Write_python_scripts#Lists

	def onInit(self):
		pass


	def onClick(self, id):

		if id == 110:
			#notification = xbmcgui.Dialog()
			#notification.ok("you clicked on the button!", "yes you did")

			# start device scan
			xbmc.log("start scan")
			self.bluetooth.scan_devices()
			xbmc.log("started scan...")


	# Called for each bluetooth device found
	def device_found(self, addr, property):

		xbmc.log("device found!")

		# Create listitem
		item = xbmcgui.ListItem()
		item.setLabel(property.get("Name", "Unknown"))
		item.setProperty("address", property.get("Address", "Unknown"))
		item.setProperty("paired", ("Yes" if property.get("Paired") else "No") )
		item.setProperty("connected", "Unknown (TODO)")
		item.setProperty("trusted", ("Yes" if property.get("Trusted") else "No"))
		item.setIconImage(DEVICE_ICON.get(property.get("Icon", "unknown")))

		# Attach item to list
		itemlist = self.getControl(ID_DEVICE_LIST)
		itemlist.addItem(item)

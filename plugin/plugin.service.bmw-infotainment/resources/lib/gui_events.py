"""
This module is an interface between script -and service module,
using cPython library "libguicallback.so" for handling callbacks.
"""

import libguicallback as guicallback

__author__ = 'Lars'


class Callback(object):

	"""
	Set callbacks handlers from the GUI.
	"""

	def __init__(self, service):

		self.service = service

	def init_callbacks(self):

		guicallback.setOnConnect(self.service.request_start)
		guicallback.setOnDisconnect(self.service.request_stop)

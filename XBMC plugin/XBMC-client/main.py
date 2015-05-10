__author__ = 'Lars'

# from lib.KodiControls import Controls

# import client lib
from lib.TCPClientHandler import *

import threading
import logging

# set up logging&/debug handler
# https://docs.python.org/2/howto/logging-cookbook.html

# setup basic logging configs
# TODO: migrate this to settings?
logging.basicConfig(level=logging.DEBUG,
					format='%(asctime)s %(name)-12s %(levelname)-8s %(message)s',
					datefmt='%m-%d %H:%M')

# create formatter and add it to the handlers
#formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')

# create log object
log = logging.getLogger('KODI-client')

# output to console
console = logging.StreamHandler()
#console.setLevel(logging.DEBUG)

# add a handler to log object
log.addHandler(console)

# some connection data
# TODO: use a separate setting file?
HOST = '192.168.1.68'
PORT = 4287
RECONNECT = 3

client = MsgHandler(HOST, PORT)

# the actual server thread.
def TCPClientThread():
	while (client.reconnections < RECONNECT):

		client.reconnections += 1

		# Init the TCP connection
		client.init_connect()
		asyncore.loop()
		log.info("Connection lost... Try reconnecting (attempt %s of %s)..", client.reconnections, RECONNECT )

# Launch gateway on Raspberry Pi:
# ./gateway -d /dev/ttyUSB0 -i 0.0.0.0



# if file is executed (not included)
if __name__ == "__main__":

	# launch the server thread.
	threading.Thread( name='TCPServerThread', target=TCPClientThread ).start()


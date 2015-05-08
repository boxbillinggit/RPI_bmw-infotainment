import socket, binascii, threading

# message struct (8-byte header):

# -----------------------------
# 
# -----------------------------
# create a 'threaded server':
# https://docs.python.org/2/library/socketserver.html

HOST = '192.168.1.68'
PORT = 4287

# ping message
PING_TIME = 3
PING = bytearray([0xAA, 0xAA, 0, 0, 0, 0, 0, 0])
INIT = bytearray(['h', 'i', 0, 0, 0, 0, 0, 0])

ACK_CONNECTED = 'ct'

# don't understand this init
#ibus = socket.socket(socket.AF_INET, socket.SOCK_RAW, socket.IPPROTO_IP)

# create socket object
ibus = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

# 1:st connect (get a available port)
ibus.connect((HOST, PORT))
ibus.send(INIT)
buf = ibus.recv(16)
ibus.close()

#TODO: check received ACK. if no ack is received, disconnect..
# http://stackoverflow.com/questions/8600161/executing-periodic-actions-in-python

def send_ping():
	print "sending ping..."
	ibus.send(PING)
	# ack
	buf = ibus.recv(16)
	print(str(buf[0] + buf[1]).encode('hex'))
	
	threading.Timer(PING_TIME, send_ping).start()
	
# get connecting port and connect.
if ( ACK_CONNECTED in buf[0:2] ):

	# 16-bit port number (in reverse order)
	new_port = int( str(buf[5]+buf[4]).encode('hex'), 16 )
	ibus = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	ibus.connect((HOST, new_port))
	
	#start ping (alive signal)
	threading.Timer(PING_TIME, send_ping).start()
	
	


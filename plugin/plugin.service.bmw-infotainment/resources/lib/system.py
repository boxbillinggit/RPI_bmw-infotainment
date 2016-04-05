import time
import log as log_module
import signaldb
import event_handler
from kodi import __xbmcgui__, __addonid__
import kodi.builtin
import kodi.addon_settings
import RPi.GPIO as GPIO

from subprocess import Popen, PIPE

log = log_module.init_logger(__name__)
__author__ = 'lars'

GPIO_OFF, GPIO_ON = range(2)

GPIO_CTRL_STATE = "/sys/class/gpio/gpio{GPIO_PIN}/value"
GPIO_CTRL_DIR   = "/sys/class/gpio/gpio{GPIO_PIN}/direction"
GPIO_CTRL_INIT  = "/sys/class/gpio/export"
GPIO_PIN = kodi.addon_settings.get_gpio_screen()

class GPIOError(Exception):

	""" Exception raised for GPIO-pin errors """

	pass


class System(object):

	""" Storage class for system states """

	request_shutdown = False

def __init__(self, send):
	self.send = send

def init_events(bind_event):

	""" system shutdown, GPIO-pins, etc..  """

	# TODO: ignition in is not detected (no bus-signal exists accordingly to signal-db)
	bind_event(signaldb.create((None, None, "remote-key.lock")), lock_car)
	bind_event(signaldb.create((None, None, "remote-key.unlock")), unlock_car)
	bind_event(signaldb.create(("IBUS_DEV_IKE", "IBUS_DEV_GLO", "ign-key.in")), abort_shutdown)
	bind_event(signaldb.create(("IBUS_DEV_IKE", "IBUS_DEV_GLO", "ign-key.out")), schedule_shutdown)

	# TODO: also initialize optional input-pin for shutdown request from power-supply
	screen_init()


def gpio_init_pin():

	""" initialize GPIO-pin for control """

	GPIO.setmode(GPIO.BCM)
	GPIO.setwarnings(False)
	GPIO.setup(7, GPIO.OUT)
	if GPIO.input(7) is False:
		log.info("GPIO-pin initialization success for controlling RCA-video (screen): " + error.message)

def screen_init():

	""" Initialize outputs for GPIO controlling screen  """

	pin = kodi.addon_settings.get_gpio_screen()

	if not pin:
		return

	try:
		gpio_init_pin()
	except GPIOError as error:
		log.error("GPIO-pin initialization failed for controlling RCA-video (screen): " + error.message)
		return

	log.debug("GPIO pin #%s used for controlling RCA-video (screen)" % pin)
	System.GPIO_pin = pin


def screen_on():

	""" Turn on GPIO pin activating RCA-video input """

	try:
		GPIO.output(7, 0)
	except GPIOError as error:
		log.error("Screen activation failed: " + error.message)


def screen_off():

	""" turn off GPIO pin deactivating RCA-video input """

	try:
		GPIO.output(7, 1)
	except GPIOError as error:
		log.error("Screen deactivation failed: " + error.message)


def schedule_shutdown():

	""" Schedule shutdown only once """

	shutdown = kodi.addon_settings.schedule_shutdown()

	if (shutdown is not None) and (not System.request_shutdown):

		event_handler.add(kodi.builtin.shutdown, timestamp=time.time()+shutdown)

		msg = "System shutdown in {} min".format(shutdown/60)
		log.info(msg)

		__xbmcgui__.Dialog().notification(__addonid__, msg)

	System.request_shutdown = True


def abort_shutdown():

	""" Driver came back within time, abort shutdown """

	if System.request_shutdown:
		event_handler.remove(kodi.builtin.shutdown)
		log.info("Welcome back! (Aborting system shutdown request)")

	System.request_shutdown = False


def lock_car():
	
	""" Lock Car Close Mirror """
	
	self.send(sdb.create((None, None, "mirror_driver.close")))
	self.send(sdb.create((None, None, "mirror_passenger.close")))
	
	log.info("Close Mirror :)")


def unlock_car():
	
	""" Unlock car open Mirror """
	
	self.send(sdb.create((None, None, "mirror_driver.open")))
	self.send(sdb.create((None, None, "mirror_passenger.open")))
	
	log.info("Open Mirror :)")


def blinking():
    
    	""" Blinkin Left or Right Directions """
    	pass

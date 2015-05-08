__author__ = 'Lars'

# This acts as the interface for controlling KODI through IBUS
# using the HTTP JSON RPC protocol (http://kodi.wiki/view/JSON-RPC_API/v6)
# reading in the signal database and ... To be continued!

from xbmcjson import XBMC
import urllib2
import xml.etree.ElementTree as XML

#
class Controls(object):

    def __init__(self, vhost="127.0.0.1", user="kodi", password="", signal_db_name="SignalDatabase.xml"):

        # setup the connection to KODI (through JSON RPC)
        host = "http://%s/jsonrpc" % (vhost)
        self.kodi = XBMC(host, user, password)

        # test connection to KODI
        self.check_response(self.kodi.JSONRPC.Ping)

        # read in signal database
        self.signal_db = None
        self.signal_db_name = signal_db_name
        self.read_signal_db()

        # add IBUS event listeners
        #self.add_event_listeners()

    # read in signal database
    def read_signal_db(self):
        try:
            self.signal_db = XML.parse(self.signal_db_name)
        except IOError as err:
            print err

    # check JSON respone back from KODI
    def check_response(self, execute):

        try:
            response = execute()

            # could not connect
            if response.has_key("error"):
                print response

        except urllib2.URLError as err:
            print err
        except:
            print "Unknown error"


    def add_event_listeners(self, signal_db="SignalDatabase.xml"):

        # read in the signal database.
        tree = XML.parse(signal_db)

        # generate list of messages to listen to ?
        my_list = dict()

        #list is containing src, dst, data, "name of event"

        return my_list


    def IBUSListener(self, msg):


        # or based on state ex: right-knob.STATE ?

        # listen to these messages
        listen_to = {
            # "event-id": name_constructor()
            "event": "right-knob.release",  # TODO: should be auto-named event? as example: "right-knob.release".
            # "button": "right-knob",
            # "state": "release"
            "raw": {"src": "IBUS_DEV_BMBT", "dst": "IBUS_DEV_GT",
                    "data": self.byte_constructor(xpath=".//button[@name='right-knob']/state[@id='release']")}
        }

        # decode push button for

        # 'Source' matters
        if msg_test.has_attr("src"):
            print "hej"

        # 'Destination' matters

        # 'data' matters

    def check_state(self):

        # event: "Select" (short push right knob)
        if True:
            self.check_response(self.kodi.JSONRPC.Select)

        # event: "back" (long push right knob)
        if False:
            self.check_response(self.kodi.JSONRPC.Back)

    def byte_constructor(self, xpath):

        result = self.signal_db.findall(xpath)

        # iterate over all sub-elements and fetch id (constructs the message)
        print result

    def button_state(self):


        self.STATE = self.INIT

        print "hej"
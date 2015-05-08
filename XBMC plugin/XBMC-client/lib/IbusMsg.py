__author__ = 'Lars'

# Decodes the signal database and route events from that.

class DecodeMsg:

    # button states
    RELEASED = 0
    PUSH = 1
    HOLD = 2

    def __init__(self):
        self.STATE = self.RELEASED

    # decode IBUS message
    def IBUSListener(self, msg):


        if True:

        print "hej"
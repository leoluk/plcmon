#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#   Copyright (c) 2012 Leopold Schabel
#   All rights reserved.
#

import sys, os
import threading
import logging
import time

from utils import nma, messaging365
from utils.datagram_constants import *

import chump

MESSAGES = {
    EVT_SYSTEM_ALARM: ('Alarmanlage', 'Alarm ausgelöst', 2),
    EVT_SYSTEM_RESET: ('Alarmanlage', 'Alarmanlage zurückgesetzt und unscharf geschaltet', 1),
    EVT_SYSTEM_LIVE: ('Alarmanlage', 'Alarmanlage scharf geschaltet', 0),
    EVT_SYSTEM_DISABLED: ('Alarmanlage', 'Alarmanlage unscharf geschaltet', 0),
}

class NotificationThread(threading.Thread):
    def __init__(self, inqueue, config):
        threading.Thread.__init__(self)
        self.inqueue = inqueue
        self.config = config
        self.logger = logging.getLogger('notify')
        self.nma = nma.NMAProvider(config['nma_keys'])
        self.chump_app = chump.Application("av8nZsoa4oqaw7a5sZ2FC9PYBKiYCK")

        self.chump_users = [self.chump_app.get_user(x) for x
                            in self.config['pover_keys']]

        self.m365 = messaging365.M365Provider(*self.config['m365_login'])

    def send_message(self, event, description, priority):

        if priority == 2:
            sound = "siren"
        else:
            sound = None

        for user in self.chump_users:
            user.send_message(description.decode('utf8'),
                              priority=priority, sound=sound)

        message = "[%s] %s: %s" % (time.strftime("%d.%m.%y %H:%M"),
                                   event, description)

        for number in self.config['phone_numbers']:
            self.m365.send_message(number, "PLCMON",
                                   message, msg_type="ussd")

        self.nma.notify(event, description, priority=priority)


    def run(self):
        while True:
            message = self.inqueue.get()

            try:
                event, description, priority = MESSAGES[message]
            except KeyError:
                self.logger.error("Invalid message: 0x%02X", message)

            try:
                self.send_message(event, description, priority=priority)
            except RuntimeError:
                self.logger.exception("Couldn't dispatch message"
                                      "to mobile devices")




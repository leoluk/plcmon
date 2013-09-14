#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#   Copyright (c) 2012 Leopold Schabel
#   All rights reserved.
#

from __future__ import unicode_literals

import threading
import logging
import time
import sqlite3

import chump

from utils import nma, messaging365
from utils.datagram_constants import *


MESSAGES = {
    EVT_SYSTEM_ALARM: ('Clubheim', 'Alarm ausgelöst', 2),
    EVT_SYSTEM_RESET: ('Clubheim', 'Alarmanlage zurückgesetzt und unscharf geschaltet', 1),
    EVT_SYSTEM_LIVE: ('Clubheim', 'Alarmanlage scharf geschaltet', 0),
    EVT_SYSTEM_DISABLED: ('Clubheim', 'Alarmanlage unscharf geschaltet', 0),
}


class NotificationThread(threading.Thread):
    def make_db(self):
        self.db_cursor.executescript("""
        CREATE TABLE IF NOT EXISTS events (
          timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
          plcmon_data INT,
          app_name TEXT,
          app_label TEXT,
          event_source TEXT,
          priority INT,
          event_text TEXT
        );
        """)
        self.db_conn.commit()

    def log_event(self, plcmon_data, event, description, priority):
        self.db_conn.execute("INSERT INTO events (plcmon_data, event_source, event_text, priority, app_name, app_label)"
                             " VALUES "
                             "(?, ?, ?, ?, ?, ?)", (plcmon_data, event, description,
                                                    priority, self.config['app_name'], self.config['label']))
        self.db_conn.commit()

    #noinspection PyArgumentList
    def __init__(self, inqueue, config):
        threading.Thread.__init__(self)
        self.inqueue = inqueue
        self.config = config
        self.logger = logging.getLogger('notify')
        self.nma = nma.NMAProvider(config['nma_keys'])
        self.chump_app = chump.Application(self.config['pover_app_id'])

        self.chump_users = [self.chump_app.get_user(x) for x
                            in self.config['pover_keys']]

        self.m365 = messaging365.M365Provider(*self.config['m365_login'])

        if 'db_file' in self.config:
            self.db_conn = sqlite3.connect(self.config['db_file'], check_same_thread=False)
            self.db_cursor = self.db_conn.cursor()
            self.make_db()


    def send_message(self, event, description, priority):

        if priority == 2:
            sound = "alien"
        else:
            sound = None

        # Send PushOver
        for user in self.chump_users:
            user.send_message(description,
                              priority=priority, sound=sound,
                              title=event)

        message = "[%s, %s] %s: %s" % (self.config['label'],
                                       time.strftime("%d.%m.%y %H:%M"),
                                       event, description)

        for number in self.config['phone_numbers']:
            # Send USSD
            self.m365.send_message(number, self.config['label'],
                                   message, msg_type="ussd")

        # Send NotifyMyAndroid
        self.nma.notify(event, description, priority=priority,
                        application=self.config['label'])

    def run(self):
        while True:
            message = self.inqueue.get()

            try:
                event, description, priority = MESSAGES[message]
            except KeyError:
                self.logger.error("Invalid message: 0x%02X", message)
                return

            try:
                self.log_event(message, event, description, priority)
                self.send_message(event, description, priority=priority)
            except RuntimeError:
                self.logger.exception("Couldn't dispatch message"
                                      "to mobile devices")




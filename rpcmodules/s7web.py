#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#   Copyright (c) 2012 Leopold Schabel
#   All rights reserved.
#

import sys, os
import thread
import time
import logging

from utils import s7comm


class CheckerThread(threading.Thread):
    def __init__(self, plc, password, delay=60):
        threading.Thread.__init__(self)
        self.plc = plc
        self.delay = delay
        self.password = password
        self.logger = logging.getLogger("plcmon.checker")

    def _periodic_check(self):
        self.logger.debug("Checking logging session...")
        if not self.plc.logged_in:
            try:
                self.logger.info("Not logged in! Relogin: %s" % self.plc.login(self.password))
            except s7comm.LoginFailure:
                self.logger.fatal("SPS login failed! exiting..")
                sys.exit(1)
        else:
            self.logger.debug("Login session valid!")

    def run(self):
        while True:
            self._periodic_check()
            time.sleep(self.delay)


def rpc_register(server, config):
    logger = logging.getLogger("rpc.s7web")

    plc = s7comm.S7WebComm(config['sps_ip'])

    checker = CheckerThread(plc, config['sps_password'])

    server.register_function(plc.read_value, 'sps_read_value')
    server.register_function(plc.read_values, 'sps_read_values')
    server.register_function(plc.set_value, 'sps_set_value')
    server.register_function(plc.set_values, 'sps_set_values')
    server.register_function(plc.sps_flash_led)
    server.register_function(plc.sps_information)
    server.register_function(plc.sps_run)
    server.register_function(plc.sps_stop)
    server.register_function(plc.sps_status)
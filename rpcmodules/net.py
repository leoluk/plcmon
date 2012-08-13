#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#   Copyright (c) 2012 Leopold Schabel
#   All rights reserved.
#
#   This copyright notice MUST APPEAR in all copies of the script!
#   In case of abuse or illegal redistribution please contact me:
#   mail@leoschabel.de
#

from utils import netscan, netstate

def rpc_register(server, config):
    server.register_function(netscan.ping_sweep)
    server.register_function(netstate.link_status)
    server.register_function(netstate.last_change)

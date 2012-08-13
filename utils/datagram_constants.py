#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#   Copyright (c) 2012 Leopold Schabel
#   All rights reserved.
#

PORT_STATUS = 7001
PORT_NOTIFY = 7002

EVT_SYSTEM_LIVE = 0x01
EVT_SYSTEM_DISABLED = 0x02
EVT_SYSTEM_ALARM = 0x3
EVT_SYSTEM_RESET = 0x4

EVENTS = {
    EVT_SYSTEM_LIVE: "Alarm system live",
    EVT_SYSTEM_DISABLED: "Alarm system disabled",
    EVT_SYSTEM_ALARM: "Alarm triggered",
    EVT_SYSTEM_RESET: "Alarm reset",
}

MAP_NOTIFY_0F = {
    0x01: EVT_SYSTEM_LIVE,
    0x0F: EVT_SYSTEM_DISABLED,
}

MAP_NOTIFY_F0 = {
    0xF0: EVT_SYSTEM_ALARM,
    0xE0: EVT_SYSTEM_RESET,
}
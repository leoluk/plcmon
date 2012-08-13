#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#   Copyright (c) 2012 Leopold Schabel
#   All rights reserved.
#

"""
Receives UDP datagrams from our custom PLC software.

There are two datagram types:

    - Status broadcast, 7001/udp

    – Notification, 7002/udp

          0x01 - Alarm system live
          0x0F - Alarm system disabled
          0xF0 - Alarm triggered
          0xE0 - Alarm reset

"""


import sys, os
import threading
import Queue
import logging
import struct

import socket_ext as socket  # PyXAPI (recvmsg)

from datagram_constants import *

NETDEBUG = 5

logging.addLevelName(NETDEBUG, "NETDEBUG")


class DatagramReceiver(threading.Thread):
    def __init__(self, port, bind="0.0.0.0"):
        threading.Thread.__init__(self)
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.sock.bind((bind, port))
        self.logger = logging.getLogger("datagram.receiver")
        self.messages = Queue.Queue()

    def run(self, packet_len):
        while True:
            sender, data, misc, flags = self.sock.recvmsg((packet_len, ))
            if flags & socket.MSG_TRUNC:
                self.logger.warn("Truncated packet from %s:%d" % sender)

            self.logger.log(NETDEBUG, "Received packet: %r", data[0])

            yield data[0]


class NotificationReceiver(DatagramReceiver):
    def __init__(self):
        DatagramReceiver.__init__(self, PORT_NOTIFY)
        self.logger = logging.getLogger("datagram.receiver.notify")

    def _dispatch(self, message):
        self.messages.put(message)
        self.logger.debug("Dispatched message %02X (%s)", message, EVENTS[message])


    def _handle_packet(self, packet, mask, lookup):
        part = packet & mask

        try:
            if part:
                self._dispatch(lookup[part])
        except KeyError:
            self.logger.warn("Invalid notify value (mask 0x%02X): 0x%02X", mask, part)


    def run(self):
        for packet in DatagramReceiver.run(self, 1):
            packet = ord(packet)

            self._handle_packet(packet, 0xF0, MAP_NOTIFY_F0)

            if not packet in REDUNDANT:
                self._handle_packet(packet, 0x0F, MAP_NOTIFY_0F)


def main():
    logging.basicConfig(stream=sys.stdout,
                        format="%(levelname)s - %(name)s -> %(message)s",
                        level=logging.DEBUG)

    notify_recv = NotificationReceiver()
    notify_recv.start()


if __name__ == '__main__':
    main()

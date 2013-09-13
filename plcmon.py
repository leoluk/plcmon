#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#   Copyright (c) 2012 Leopold Schabel
#   All rights reserved.
#

import sys, os
import threading
import time
import signal
import logging
import SocketServer
import json
from SimpleXMLRPCServer import SimpleXMLRPCServer,SimpleXMLRPCRequestHandler

# Threaded mix-in
class AsyncXMLRPCServer(SocketServer.ThreadingMixIn,SimpleXMLRPCServer): pass

# TODO: verbose log file output

logging.basicConfig(stream=sys.stdout,
        format="%(asctime)s - %(levelname)s - %(name)s -> %(message)s",
        level=logging.DEBUG if len(sys.argv)>1 else logging.INFO)

class RPCServerThread(threading.Thread):
    def __init__(self, config):
        threading.Thread.__init__(self)
        self.logger = logging.getLogger("rpc")
        self.config = config

        self.server = AsyncXMLRPCServer(('', 7878), SimpleXMLRPCRequestHandler,
                                   allow_none=True)

        self.server.register_introspection_functions()
        self.server.register_multicall_functions()

    def register_module(self, name):
        module = getattr(__import__('rpcmodules.'+name), name)

        try:
            module.rpc_register(self.server, self.config)
            self.logger.info("Registered RPC module %s" % name)
        except AttributeError:
            self.logger.error("RPC module %s has no entry point", name)

    def run(self):
        self.logger.info("Entering server loop...")
        self.server.serve_forever()


def main():
    logger = logging.getLogger("plcmon")

    logger.info("Loading configuration...")

    config = json.load(open('config.yml'))

    logger.info("Starting RPC server...")

    rpcserver = RPCServerThread(config)

    if config['rpc_module_s7web']:
        rpcserver.register_module('s7web')

    if config['rpc_module_net']:
        rpcserver.register_module('net')

    rpcserver.start()

    if config['module_notify']:
        logger.info("Loading notification module...")

        from modules import notify
        from utils import datagram

        logger.info("Starting datagram notification listener (7002/udp)...")

        listen_notify = datagram.NotificationReceiver()
        listen_notify.start()

        logger.info("Starting notification dispatcher...")

        notify_dispatcher = notify.NotificationThread(listen_notify.messages,
                                                      config)
        notify_dispatcher.start()

        notify_dispatcher.send_message("PLCMON", "Dienst gestartet",
                                       priority=-1)

    while True:
        try:
            time.sleep(1)
        except KeyboardInterrupt:
            logger.info("Shutting down...")
            # TODO: stop threads nicely
            os.kill(os.getpid(), signal.SIGKILL)

if __name__ == '__main__':
    main()

#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#   Copyright (c) 2013 Leopold Schabel
#   All rights reserved.
#

from __future__ import unicode_literals
import argparse
import sys
import json
import Queue
import logging
from modules import notify

logging.basicConfig(stream=sys.stdout,
                    format="%(asctime)s - %(levelname)s - %(name)s -> %(message)s",
                    level=logging.DEBUG)


def main():
    parser = argparse.ArgumentParser()

    parser.add_argument('title', help="Notification title")
    parser.add_argument('text', help="Notification text")
    parser.add_argument('-p', '--priority', help="Priority", default=0)

    opts = parser.parse_args()
    config = json.load(open('config.yml'))
    config['app_name'] = 'PLCMON-SendMsg'

    event = opts.title.decode('utf8')
    description = opts.text.decode('utf8')

    notifier = notify.NotificationThread(Queue.Queue(), config)

    notifier.log_event(None, event, description, opts.priority)
    notifier.send_message(event, description, opts.priority)


if __name__ == '__main__':
    main()
#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#   Copyright (c) 2012 Leopold Schabel
#   All rights reserved.
#

import sys, os
import re
import platform
import random

import envoy
import dateutil.parser
from datetime import datetime
from dateutil.relativedelta import relativedelta

UNIX = (platform.system() != 'Windows')

if not UNIX:
    import wmi
    wmic = wmi.WMI()
    INTERFACE_LIST = [u'%s-%s' % (iface.DeviceID, iface.ServiceName)
                      for iface in wmic.Win32_NetworkAdapter() if iface.NetConnectionStatus != None]
else:
    import netifaces
    INTERFACE_LIST = netifaces.interfaces()

RE_LINK = re.compile(r"Link detected: (yes|no)")
RE_LINKLOG = re.compile(r"(\w+\s+\d+ \d+:\d+:\d+) .+ kernel: eth2: link (up|down)")

# TODO: proper Windows implementation here, please!

if UNIX:
    LOGFILE_PATH = "/var/log/messages"
else:
    LOGFILE_PATH = ""


def link_status(interface="DEBUG"):
    '''Returns whether there is a physical connection on a network interface or not.

    `interface` is a device name on Linux (example: 'eth2')
        and a WMI name on Windows (example: '7-RTL8167')

    SECURITY NOTE: Input not sanitized!

    '''

    if interface == "DEBUG":
        return True

    if not interface in INTERFACE_LIST:
        raise ValueError("Interface %s not present on enumeration" % interface)

    if UNIX:
        try:
            return bool(['no', 'yes'].index(RE_LINK.search(envoy.run('ethtool '+interface).std_out).group(1)))
        except AttributeError:
            return None
    else:
        ifid, ifname = interface.split('-')
        ifaces = wmic.Win32_NetworkAdapter(DeviceID=ifid) #, ServiceName=ifname)
        # TODO: speed up

        if not ifaces:
            raise ValueError("Interface %s could not be found" % interface)

        return bool( ifaces[0].NetConnectionStatus < 4
                  or ifaces[0].NetConnectionStatus > 7)


def last_change(interface, logfile=LOGFILE_PATH, ):
    """Scans the system log for the most recent up/down event of the specified interface
    and returns a tuple with the timestamp (as datetime) and the event (i.e. up/down).

    Returns None when no matching event was found.

    `logfile`: the syslog to search
    `interface`: the interface to search for

    """

    # TODO: search rotated log files as well
    # TODO: clean up Windows mess a little bit

    ### DEBUG CODE ###

    if not UNIX:
        if ('WINGDB_ACTIVE' in os.environ) or (interface == "DEBUG"):
            return datetime.now()+relativedelta(hours=-random.randint(1,5)), link_status(interface)
        else:
            return None

    ### END DEBUG CODE ###

    try:
        logentry = filter(lambda x: ("%s: link" % interface) in x,
                      open(logfile).readlines())[-1]
    except IndexError:
        return None

    timestr, event = RE_LINKLOG.search(logentry).groups()

    return dateutil.parser.parse(timestr), event


def main():
    from pprint import pprint

    print "Enumerated network interfaces:"
    pprint(INTERFACE_LIST)

    for iface in INTERFACE_LIST:
        print "Link status for interface %s:" % iface, link_status(iface)

        if last_change(iface):
            print "Last status change for interface %s:" % iface, last_change(iface)


if __name__ == '__main__':
    main()